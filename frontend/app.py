import os
import json
import re
import spacy
from spacy.cli import download
import subprocess
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv

# === Load spaCy ===
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("🔁 'en_core_web_sm' not found. Downloading...")
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# === Load secrets ===
load_dotenv()
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
NEO4J_URI = st.secrets.get("NEO4J_URI", os.getenv("NEO4J_URI"))
NEO4J_USER = st.secrets.get("NEO4J_USERNAME", os.getenv("NEO4J_USERNAME"))
NEO4J_PASS = st.secrets.get("NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD"))

# === Neo4j Setup ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

# === Load chunks ===
CHUNKS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chunks.json")
try:
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
except:
    chunks = []

# === Utility ===
def sanitize_relation(verb):
    verb = verb.strip().upper().replace(" ", "_").replace("-", "_")
    return re.sub(r"[^A-Z0-9_]", "", verb) or "RELATED_TO"

# === Query Neo4j ===
def query_neo4j(question):
    keywords = [word for word in question.split() if len(word) > 3]
    with driver.session() as session:
        for kw in keywords:
            result = session.run("""
                MATCH (a:Entity)-[r]->(b:Entity)
                WHERE toLower(a.name) CONTAINS toLower($kw)
                RETURN a.name, type(r), b.name LIMIT 1
            """, kw=kw)
            record = result.single()
            if record:
                return f"({record['a.name']}) -[{record['type(r)']}] -> ({record['b.name']})"
    return ""

# === RAG Query ===
def query_rag(text):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

    matched_chunk = None
    query_words = set(text.lower().split())
    max_match = 0
    for chunk in chunks:
        content = chunk.get("text") or chunk.get("chunk") or ""
        score = sum(1 for word in query_words if word in content.lower())
        if score > max_match:
            max_match = score
            matched_chunk = content

    if not matched_chunk:
        return "⚠️ No relevant content found."

    prompt = f"""
You are a helpful assistant for MOSDAC satellite data.
Use the context below to answer the question:

Context:
{matched_chunk}

Q: {text}
A:
"""

    try:
        model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"❌ Gemini error: {e}"

# === Intent Detection ===
def detect_intent(text):
    lowered = text.lower()
    if any(w in lowered for w in ["map", "location", "where"]):
        return "geo"
    elif any(t.dep_ == "nsubj" for t in nlp(text)):
        return "kg"
    return "rag"

# === Streamlit UI ===
st.set_page_config(page_title="SkyQuery AI", page_icon="🛰️", layout="wide")
st.title("🛰️ SkyQuery AI Help Bot")
st.caption("Ask me about satellite missions, weather data, or geo info from MOSDAC")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if query := st.chat_input("Ask me about Oceansat-3, INSAT, weather, etc..."):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    intent = detect_intent(query)
    if intent == "kg":
        response = query_neo4j(query)
    elif intent == "rag":
        response = query_rag(query)
    else:
        response = "🌍 Here's a sample location for visualization"

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)

        if intent == "geo":
            lat, lon = 23.0, 72.0  # default location (e.g., Gujarat)
            m = folium.Map(location=[lat, lon], zoom_start=6)
            folium.Marker([lat, lon], popup=query).add_to(m)
            st_folium(m, height=400)
