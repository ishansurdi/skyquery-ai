import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# 🔐 Load .env variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

# 🔧 Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# 📄 Load data chunks
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_PATH = os.path.join(PROJECT_ROOT, "data", "chunks.json")

try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
except FileNotFoundError:
    print(f"❌ chunks.json not found at {CHUNKS_PATH}")
    chunks = []

# 🤖 Main RAG Query Function
def query_rag(query_text: str) -> str:
    query_text = query_text.strip()
    if not query_text:
        return "⚠️ Please enter a valid question."

    # Handle greetings or vague inputs
    if query_text.lower() in {"hey", "hi", "hello", "okay"}:
        return "👋 Hello! Ask me something like 'What is Oceansat-3?' or 'Show me Gujarat on map.'"

    query_words = set(query_text.lower().split())
    matched_chunk = None
    max_match_score = 0

    # 🧠 Match query with best chunk
    for chunk in chunks:
        text = chunk.get("text") or chunk.get("chunk") or ""
        if not text.strip():
            continue

        text_lower = text.lower()
        match_score = sum(1 for word in query_words if word in text_lower)

        if match_score > max_match_score:
            matched_chunk = text.strip()
            max_match_score = match_score

    if not matched_chunk:
        return "⚠️ No relevant information found in MOSDAC content."

    # 📨 Prompt for Gemini
    prompt = f"""
You are a helpful AI assistant with expertise in Indian satellite data and MOSDAC services.

Answer the user's question using the following context:

---
{matched_chunk}
---

Q: {query_text}
A:"""

    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
        

    except Exception as e:
        return f"❌ Gemini failed to answer: {e}"
