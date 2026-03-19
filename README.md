# 🤖 RAG Agent — מערכת שאלות ותשובות חכמה

מערכת AI המאפשרת שאילתות חכמות על מסמכי תיעוד טכני באמצעות ארכיטקטורת **RAG** (Retrieval-Augmented Generation).

המערכת משלבת **Event-Driven Workflow**, **חיפוש סמנטי** ב-Pinecone, ו**שליפה מובנית** מ-JSON — ומחליטה אוטומטית איזו שיטה מתאימה לכל שאלה.

---

## 🏗️ ארכיטקטורה

```
שאלת משתמש
     │
     ▼
┌─────────────────┐
│  Retrieve Step  │  ← בודק אם שאלת שיחה / קצרה מדי
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │   Router   │  ← מחליט: structured או semantic?
    └─────┬──────┘
          │
    ┌─────┴──────┐
    │            │
    ▼            ▼
┌────────┐  ┌──────────┐
│  JSON  │  │ Pinecone │
│ שליפה │  │  חיפוש  │
└────┬───┘  └────┬─────┘
     │            │
     └─────┬──────┘
           ▼
   ┌───────────────┐
   │ Generate Step │  ← מנסח תשובה סופית בעברית
   └───────┬───────┘
           ▼
      תשובה למשתמש
```

---

## 🚀 התקנה והפעלה

### דרישות מקדימות

- Python 3.10+
- חשבון [Cohere](https://cohere.com/) עם API Key
- חשבון [Pinecone](https://www.pinecone.io/) עם API Key ו-Index בשם `my-rag-index`

### התקנת תלויות

```bash
pip install llama-index llama-index-llms-cohere llama-index-embeddings-cohere
pip install llama-index-vector-stores-pinecone pinecone-client
pip install gradio python-dotenv
```

### הגדרת משתני סביבה

צרי קובץ `.env` בתיקיית הפרויקט:

```env
COHERE_API_KEY=your_cohere_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=my-rag-index
```

### הכנת הנתונים (פעם ראשונה)

```bash
python reset_pinecone.py
python extract_data.py
```

### הרצת הממשק

```bash
python main.py
```

פתחי את הדפדפן בכתובת: `http://127.0.0.1:7860`

---

## 📁 מבנה הפרויקט

```
my_rag_project/
├── main.py              # ממשק Gradio + Workflow ראשי
├── router.py            # ניתוב בין חיפוש סמנטי לשליפה מובנית
├── extract_data.py      # חילוץ נתונים מובנים מהמסמכים
├── reset_pinecone.py    # איפוס והעלאת נתונים ל-Pinecone
├── extracted_data.json  # נתונים מובנים
├── .env                 # מפתחות API (לא מועלה ל-GitHub)
├── .gitignore
└── data/
    ├── README.md
    ├── development_plan.md
    └── song_catalog_technical_documentation.md
```

---

## 💬 דוגמאות לשאלות

### שאלות רשימתיות ← שליפה מ-JSON
```
תני לי את כל האזהרות בפרויקט
רשמי את כל הפיצ'רים המתוכננים
מה כל ההחלטות הטכניות שהתקבלו?
```

### שאלות הסבר ← חיפוש סמנטי ב-Pinecone
```
איך עובד הסינון לפי חודש עברי?
מה זה localStorage ואיך הוא משמש כאן?
איך מתבצעת עריכת שיר?
```

---

## 🛠️ טכנולוגיות

| רכיב | טכנולוגיה |
|------|-----------|
| LLM | Cohere `command-r7b-12-2024` |
| Embeddings | Cohere `embed-multilingual-v3.0` |
| Vector DB | Pinecone |
| Framework | LlamaIndex |
| Workflow | LlamaIndex Event-Driven Workflow |
| UI | Gradio |

---

## ⚠️ מגבלות ידועות

- המודל מדי פעם מערבב שפות — מטופל ע"י הוראות מפורשות בפרומפט
- שאלות עם ניסוחים מורכבים עלולות להיות מנותבות לא נכון
- בשינוי מסמכים יש להריץ מחדש את `reset_pinecone.py`