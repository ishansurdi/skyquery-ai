# prepare_chunks.py

import os
import json
import pdfplumber
from docx import Document
import pandas as pd

from pathlib import Path
from tqdm import tqdm

# === Auto-detect project root ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# === Absolute Paths ===
ALL_PAGES = os.path.join(PROJECT_ROOT, "crawler", "all_pages.txt")
DOC_DIR = os.path.join(PROJECT_ROOT, "crawler", "downloads")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "chunks.json")

# === Ensure output directory exists ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Chunking Parameters ===
MAX_CHUNK_WORDS = 400
OVERLAP = 50

def chunk_text(text, max_words=MAX_CHUNK_WORDS, overlap=OVERLAP):
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words - overlap):
        chunk = " ".join(words[i:i+max_words])
        if len(chunk.strip()) > 50:  # Skip tiny chunks
            chunks.append(chunk)
    return chunks

# === Parse all_pages.txt ===
def parse_all_pages():
    chunks = []
    with open(ALL_PAGES, "r", encoding="utf-8") as f:
        content = f.read()
        sections = content.split("🌐 URL: ")
        for sec in sections[1:]:
            try:
                url, body = sec.split("\n", 1)
                page_chunks = chunk_text(body)
                for ch in page_chunks:
                    chunks.append({
                        "chunk": ch,
                        "source": url.strip(),
                        "type": "web"
                    })
            except Exception as e:
                print(f"[!] Skipped malformed section: {e}")
    return chunks

# === Parse PDF ===
def parse_pdf(path):
    try:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return chunk_text(text)
    except Exception as e:
        print(f"[PDF Error] {path}: {e}")
        return []

# === Parse DOCX ===
def parse_docx(path):
    try:
        doc = Document(path)
        text = "\n".join([p.text for p in doc.paragraphs])
        return chunk_text(text)
    except Exception as e:
        print(f"[DOCX Error] {path}: {e}")
        return []

# === Parse XLSX ===
def parse_xlsx(path):
    try:
        dfs = pd.read_excel(path, sheet_name=None)
        text = "\n".join([df.to_string(index=False) for df in dfs.values()])
        return chunk_text(text)
    except Exception as e:
        print(f"[XLSX Error] {path}: {e}")
        return []

# === Parse all documents in crawler/downloads ===
def parse_documents():
    chunks = []
    for file in tqdm(os.listdir(DOC_DIR), desc="📄 Parsing documents"):
        path = os.path.join(DOC_DIR, file)
        ext = Path(file).suffix.lower()
        chunk_list = []

        if ext == ".pdf":
            chunk_list = parse_pdf(path)
        elif ext == ".docx":
            chunk_list = parse_docx(path)
        elif ext == ".xlsx":
            chunk_list = parse_xlsx(path)

        for ch in chunk_list:
            chunks.append({
                "chunk": ch,
                "source": file,
                "type": ext.replace(".", "")
            })
    return chunks

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Preparing chunks from all data sources...")

    all_chunks = []
    all_chunks += parse_all_pages()
    all_chunks += parse_documents()

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"✅ Done. {len(all_chunks)} chunks saved to {OUTPUT_JSON}")
