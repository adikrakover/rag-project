import os
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.cohere import CohereEmbedding

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

Settings.embed_model = CohereEmbedding(api_key=COHERE_API_KEY, model_name="embed-multilingual-v3.0")

# 1. התחברות ל-Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# 2. מחיקת כל הנתונים הישנים
print("מוחק נתונים ישנים מ-Pinecone...")
pinecone_index.delete(delete_all=True)
print("נמחק!")

# 3. העלאת הנתונים החדשים
print("טוען קבצים חדשים...")
documents = SimpleDirectoryReader("./data").load_data()
parser = TokenTextSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex(nodes, storage_context=storage_context)

print("הועלה בהצלחה! עכשיו הנתונים נקיים.")