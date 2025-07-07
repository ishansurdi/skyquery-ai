import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 🔑 Load .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# ⚙️ Configure Google Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 📁 Load chunks
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_PATH = os.path.join(PROJECT_ROOT, "data", "chunks.json")

try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
except FileNotFoundError:
    print(f"❌ chunks.json not found at {CHUNKS_PATH}")
    chunks = []

def query_rag(query_text: str) -> str:
    if not query_text.strip():
        return "⚠️ Please enter a valid question."

    query_words = set(query_text.lower().split())
    matched_chunk = None

    for chunk in chunks:
        text = chunk.get("text") or chunk.get("chunk") or ""
        if not text.strip():
            continue
        if any(word in text.lower() for word in query_words):
            matched_chunk = text.strip()
            break

    if not matched_chunk:
        return "⚠️ No relevant context found in the documents."

    prompt = f"""
You are a helpful assistant with access to satellite data and content from MOSDAC.

Context:
{matched_chunk}

Question:
{query_text}

Please give a short and clear answer:
"""

    try:
        # 🧠 Use Gemini Flash 1.5 or 2.0 model
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        return f"🧠 Gemini Answer:\n{response.text.strip()}"

    except Exception as e:
        return f"❌ Gemini failed: {e}"
