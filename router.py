import json
import os
from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage
from llama_index.llms.cohere import Cohere

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
llm = Cohere(api_key=COHERE_API_KEY, model="command-r7b-12-2024")

# טעינת ה-JSON
with open("extracted_data.json", "r", encoding="utf-8") as f:
    structured_data = json.load(f)


def route_query(query: str) -> str:
    """מחזיר 'structured' או 'semantic' לפי סוג השאלה"""
    response = llm.chat(messages=[ChatMessage(
        role="user",
        content=(
            f"Classify this question into one of two categories:\n"
            f"- 'structured': if it asks for a LIST, ALL items, warnings, decisions, features, or specific items by category\n"
            f"- 'semantic': if it asks HOW something works, WHY, explanation, or general question\n\n"
            f"Question: {query}\n"
            f"Answer with only one word: structured or semantic"
        )
    )], max_tokens=5)

    result = response.message.content.strip().lower()
    return "structured" if "structured" in result else "semantic"


def query_structured(query: str) -> str:
    """שליפה מה-JSON המובנה"""
    response = llm.chat(messages=[ChatMessage(
        role="user",
        content=(
            f"Answer in Hebrew only, based ONLY on this JSON data.\n"
            f"Data: {json.dumps(structured_data, ensure_ascii=False)}\n\n"
            f"Question: {query}"
        )
    )], max_tokens=300)
    return response.message.content


# בדיקה
if __name__ == "__main__":
    tests = [
        "תני לי את כל האזהרות בפרויקט",
        "איך עובד הסינון לפי חודש עברי?",
        "רשמי את כל הפיצ'רים המתוכננים",
        "מה זה localStorage?"
    ]

    for q in tests:
        route = route_query(q)
        print(f"שאלה: {q}")
        print(f"ניתוב: {route}")
        print("---")