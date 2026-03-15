import os
import json
import asyncio
import gradio as gr
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step, Event
from llama_index.core.llms import ChatMessage
from router import route_query, query_structured

# טעינת משתני סביבה
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# טעינת ה-JSON
with open("extracted_data.json", "r", encoding="utf-8") as f:
    structured_data = json.load(f)

# 2. הגדרת המודלים
Settings.embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-multilingual-v3.0")
Settings.llm = Cohere(api_key=COHERE_API_KEY, model="command-a-03-2025")
# 3. הכנת התשתית (Retriever)
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
index = VectorStoreIndex.from_vector_store(vector_store)
retriever = index.as_retriever(similarity_top_k=3)


# 4. הגדרת ה-Workflow
class RetrieveEvent(Event):
    context: str
    query: str


class RAGWorkflow(Workflow):

    @step
    async def retrieve(self, ev: StartEvent) -> RetrieveEvent | StopEvent:
        query = ev.get("query", "").strip()
        print(f"DEBUG: השאלה: '{query}'")

        if not query or len(query) < 5:
            return StopEvent(result="השאלה קצרה מדי. אנא כתבי לפחות 5 תווים.")

        # בדיקה אם השאלה קשורה לפרויקט
        check = await Settings.llm.achat(
            messages=[ChatMessage(
                role="user",
                content=(
                    f"Is this ONLY casual small talk with no technical content? "
                    f"Examples of small talk: 'how are you', 'what's up', 'good morning', 'you're funny'.\n"
                    f"Question: {query}\n"
                    f"Answer only: yes or no"
                )
            )],
            max_tokens=5
        )
        if "yes" in check.message.content.lower():
            return StopEvent(result="אני סייען טכני לפרויקט קטלוג השירים בלבד. אנא שאלי שאלה על הפרויקט.")
        # ניתוב — structured או semantic
        route = route_query(query)
        print(f"ניתוב: {route}")

        if route == "structured":
            # שליפה מה-JSON
            result = query_structured(query)
            return StopEvent(result=result)
        else:
            # חיפוש סמנטי ב-Pinecone
            nodes = retriever.retrieve(query)
            if not nodes:
                return StopEvent(result="לא מצאתי מידע רלוונטי.")
            context = "\n".join([n.get_content() for n in nodes])
            return RetrieveEvent(context=context, query=query)
    @step
    async def generate(self, ev: RetrieveEvent) -> StopEvent:
        print("Workflow: מנסח תשובה סופית...")

        context = ev.context[:1500]

        user_message = (
            f"IMPORTANT: Reply ONLY in Hebrew. Not Arabic, not Chinese, not English.\n"
            f"If you write even one word in another language, that is an error.\n"
            f"Answer in 2-3 sentences maximum. Do not repeat yourself.\n\n"
            f"Context: {context}\n\n"
            f"Question: {ev.query}"
        )

        response = await Settings.llm.achat(
            messages=[ChatMessage(role="user", content=user_message)],
            max_tokens=200
        )

        return StopEvent(result=response.message.content)

# יצירת מופע של ה-Workflow
rag_wf = RAGWorkflow(timeout=60)


# 5. פונקציית העזר עבור Gradio
async def run_chat(message, history):
    result = await rag_wf.run(query=message)
    return result


# 6. ממשק Gradio
view = gr.ChatInterface(
    fn=run_chat,
    title="סייען ה-AI שלי (Event-Driven)",
    description="מערכת RAG מבוססת Workflow ואירועים כפי שנדרש בשלב ב'",
)

if __name__ == "__main__":
    view.launch()