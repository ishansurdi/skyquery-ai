# backend/kg_interface.py

import os
import json
import spacy
import re
from neo4j import GraphDatabase
from pathlib import Path
from dotenv import load_dotenv


# === Load spaCy NLP Model ===
nlp = spacy.load("en_core_web_sm")

# === Neo4j AuraDB Credentials ===
NEO4J_URI = "neo4j+s://385a2f7a.databases.neo4j.io"
NEO4J_USER = "neo4j"

NEO4J_PASS = ""  # Replace this securely

# === Load chunked data ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK_FILE = os.path.join(PROJECT_ROOT, "data", "chunks.json")

# === Connect to Neo4j Aura ===
driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USER, NEO4J_PASS),
    connection_timeout=30
)

try:
    driver.verify_connectivity()
    print("✅ Connected to Neo4j AuraDB")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)
#== Neo4j Query == 
# def query_neo4j(question):
#     """
#     Simple query function for Neo4j:
#     It extracts named entities from the question, and finds direct relations.
#     """
#     doc = nlp(question)
#     entities = [ent.text for ent in doc.ents]

#     if len(entities) < 1:
#         return "No valid entity found in question."

#     with driver.session() as session:
#         results = []
#         for entity in entities:
#             query = """
#             MATCH (a:Entity {name: $name})-[r]->(b)
#             RETURN a.name AS source, type(r) AS relation, b.name AS target
#             LIMIT 5
#             """
#             res = session.run(query, name=entity)
#             for record in res:
#                 source = record["source"]
#                 relation = record["relation"]
#                 target = record["target"]
#                 results.append(f"({source}) -[{relation}]-> ({target})")

#         if results:
#             return "\n".join(results)
#         else:
#             return "No relationships found for the entity/entities."

def query_neo4j(question: str) -> str:
    from neo4j import GraphDatabase
    keywords = [word for word in question.split() if len(word) > 3]  # basic filter

    with driver.session() as session:
        for kw in keywords:
            result = session.run(
                "MATCH (a:Entity)-[r]->(b:Entity) "
                "WHERE toLower(a.name) CONTAINS toLower($kw) "
                "RETURN a.name, type(r), b.name LIMIT 1",
                kw=kw
            )
            record = result.single()
            if record:
                return f"{record['a.name']} --[{record['type(r)']}]--> {record['b.name']}"

    return ""


# === Valid entity types ===
ALLOWED_ENTITY_TYPES = {"ORG", "GPE", "PERSON", "NORP", "FAC", "PRODUCT", "LOC", "DATE", "EVENT"}

def sanitize_relation(verb):
    """Sanitize relation for Cypher."""
    verb = verb.strip().upper().replace(" ", "_").replace("-", "_")
    return re.sub(r"[^A-Z0-9_]", "", verb) or "RELATED_TO"

def extract_entities(doc):
    return [(ent.text.strip(), ent.label_) for ent in doc.ents if ent.label_ in ALLOWED_ENTITY_TYPES]

def extract_triples(text):
    doc = nlp(text)
    triples = []
    for sent in doc.sents:
        subj = obj = verb = ""
        for token in sent:
            if "subj" in token.dep_:
                subj = token.text
            if "obj" in token.dep_:
                obj = token.text
            if token.pos_ == "VERB":
                verb = token.lemma_
        if subj and verb and obj:
            triples.append((subj.strip(), verb.strip(), obj.strip()))
    return triples

def create_graph_node(tx, name, label):
    tx.run("MERGE (e:Entity {name: $name, label: $label})", name=name, label=label)

def create_graph_relation(tx, subj, verb, obj):
    rel_type = sanitize_relation(verb)
    query = f"""
    MATCH (a:Entity {{name: $subj}})
    MATCH (b:Entity {{name: $obj}})
    MERGE (a)-[:{rel_type}]->(b)
    """
    tx.run(query, subj=subj, obj=obj)

def process_chunk(chunk):
    text = chunk.get("text") or chunk.get("chunk") or ""
    if not text.strip():
        return
    doc = nlp(text)
    source = chunk.get("source", "unknown")

    with driver.session() as session:
        for ent, label in extract_entities(doc):
            session.execute_write(create_graph_node, ent, label)

        triples = extract_triples(text)
        if triples:
            print(f"   🔗 {len(triples)} triples from {source}")
        for subj, verb, obj in triples:
            print(f"      📎 ({subj}) -[{sanitize_relation(verb)}]-> ({obj})")
            session.execute_write(create_graph_node, subj, "Entity")
            session.execute_write(create_graph_node, obj, "Entity")
            session.execute_write(create_graph_relation, subj, verb, obj)

def main():
    if not Path(CHUNK_FILE).exists():
        print(f"❌ chunks.json not found at {CHUNK_FILE}")
        return

    print("🚀 Building Knowledge Graph from chunks...")

    with open(CHUNK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, chunk in enumerate(data):
        print(f"\n→ Processing chunk {i + 1}/{len(data)} from {chunk.get('source', 'unknown')}")
        try:
            process_chunk(chunk)
        except Exception as e:
            print(f"  ⚠️ Error in chunk {i + 1}: {e}")

    print("\n✅ Knowledge Graph successfully built in Neo4j!")

if __name__ == "__main__":
    main()
