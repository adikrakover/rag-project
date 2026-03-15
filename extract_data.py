import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.cohere import Cohere
from llama_index.core.llms import ChatMessage

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
llm = Cohere(api_key=COHERE_API_KEY, model="command-r7b-12-2024")

# 1. קריאת הקבצים
documents = SimpleDirectoryReader("./data").load_data()
full_text = "\n\n".join([doc.text for doc in documents])

def extract_category(category_name, instruction):
    prompt = f"""You are a data extraction assistant. 
Read the Hebrew documentation below and extract {category_name}.

CRITICAL RULES:
- Return ONLY a valid JSON array
- Keep all Hebrew text EXACTLY as it appears in the source - do NOT encode or escape Hebrew characters
- No markdown, no explanation, just the JSON array
- Each item must have: id (string like "dec-001"), title (Hebrew), description (Hebrew), source_file (string)

{instruction}

Documentation:
{full_text[:5000]}

Return the JSON array now:"""

    response = llm.chat(messages=[ChatMessage(role="user", content=prompt)])
    raw = response.message.content.strip()
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else parts[0]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    return json.loads(raw)

print("מחלץ החלטות...")
decisions = extract_category(
    "technical decisions",
    "Extract all technical decisions (e.g. choosing localStorage, Electron, security approach)"
)

print("מחלץ אזהרות...")
warnings = extract_category(
    "warnings and known issues",
    "Extract all warnings, known bugs, and known problems"
)

print("מחלץ תכונות...")
features = extract_category(
    "app features",
    "Extract all features - both existing and planned"
)

data = {
    "schema_version": "1.0",
    "generated_at": datetime.now().isoformat(),
    "items": {
        "decisions": decisions,
        "warnings": warnings,
        "features": features
    }
}

def fix_encoding(text):
    try:
        return text.encode('latin-1').decode('utf-8')
    except:
        return text

def fix_json_encoding(obj):
    if isinstance(obj, str):
        return fix_encoding(obj)
    elif isinstance(obj, dict):
        return {k: fix_json_encoding(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_json_encoding(i) for i in obj]
    return obj

data = fix_json_encoding(data)

with open("extracted_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nהנתונים נשמרו!")
print(f"החלטות: {len(decisions)}")
print(f"אזהרות: {len(warnings)}")
print(f"תכונות: {len(features)}")