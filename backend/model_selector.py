# backend/model_selector.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from nlp_engine import detect_intent_and_entities
from kg_interface import query_neo4j
from rag_pipeline import query_rag
from geo_module.geo_utils import query_geo


# def route_query(query_text: str):
#     intent, entities = detect_intent_and_entities(query_text)

#     print(f"[INFO] Detected intent: {intent}, Entities: {entities}")

#     if intent == "kg":
#         return query_neo4j(query_text)
#     elif intent == "rag":
#         return query_rag(query_text)
#     elif intent == "geo":
#         return query_geo(query_text)
#     else:
#         return "Sorry, I couldn't understand your query."

def route_query(question: str) -> str:
    intent, entities = detect_intent_and_entities(question)

    if intent == "geo":
        return query_geo(question)

    if intent == "kg":
        answer = query_neo4j(question)
        if answer:
            return f"🔎 KG Answer: {answer}"
        else:
            fallback = query_rag(question)
            return f"🧠 Fallback RAG Answer: {fallback}"

    # Default to RAG for general queries
    return f"🧠 RAG Answer: {query_rag(question)}"