# backend/nlp_engine.py

import spacy

# Load spaCy English model
nlp = spacy.load("en_core_web_sm")

# Keywords to identify intent categories
GEO_KEYWORDS = ["map", "region", "location", "coordinates", "area", "where", "place", "boundary", "state", "district"]
KG_VERBS = ["is", "was", "are", "relate", "define", "connect", "associate"]
RAG_KEYWORDS = ["explain", "describe", "document", "how", "why", "detail"]

def detect_intent_and_entities(text):
    doc = nlp(text)
    lowered = text.lower()

    # Extract named entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Detect intent
    if any(word in lowered for word in GEO_KEYWORDS):
        intent = "geo"
    elif any(token.dep_ == "nsubj" for token in doc) and any(token.pos_ == "VERB" and token.lemma_ in KG_VERBS for token in doc):
        intent = "kg"
    else:
        intent = "rag"

    # Optional: Print for debug
    print(f"🔍 Input: {text}")
    print(f"📌 Intent: {intent}")
    print(f"🧠 Entities: {entities}")

    return intent, entities
