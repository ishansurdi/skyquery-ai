# SkyQuery AI Help Bot

SkyQuery AI is an intelligent assistant that helps users explore satellite data, geospatial information, and knowledge from [MOSDAC](https://www.mosdac.gov.in). It combines NLP-powered Knowledge Graph querying, Retrieval-Augmented Generation (RAG) with Gemini, and Geospatial visualizations to answer natural language questions.

---

## 🌍 Features

- **🔍 Natural Language Querying:** Ask questions in plain English about satellites, products, weather, and more.
- **🧬 Intent Classification + Entity Detection:** NLP engine built with spaCy to classify queries into RAG, KG, or Geo types.
- **🔗 Neo4j Knowledge Graph:** Facts and relationships are extracted and stored as triples.
- **🔮 RAG with Gemini:** Uses Google Gemini (via API key) to answer open-ended questions based on MOSDAC data.
- **🌎 Map Integration (Folium):** Visual display of geospatial queries (e.g., location, region coverage).
- **🎨 Beautiful UI:** Streamlit chat interface, interactive responses with optional maps and extracted triples.

---

## 📁 Project Structure

```
skyquery-ai/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── nlp_engine.py        # spaCy-based NLP intent/entity detector
│   ├── model_selector.py    # Routes to KG or RAG or Geo pipeline
│   ├── kg_interface.py      # Triple extraction and Neo4j interface
│   ├── rag_pipeline.py      # Gemini-based RAG querying
│   └── geo_utils.py         # Geo location parsing & response
├── frontend/
│   └── app.py               # Streamlit interface with chat & map
├── data/
│   └── chunks.json          # Preprocessed MOSDAC content (chunked)
├── .env                     # Store API keys and secrets (Gemini, Neo4j)
├── requirements.txt         # All project dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/skyquery-ai.git
cd skyquery-ai
```

### 2. Install Dependencies

#### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

#### Frontend Setup

```bash
cd ../frontend
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```
NEO4J_PASSWORD=your_neo4j_password_here
API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

- The backend API will be available at: [http://localhost:8000](http://localhost:8000)
- Test endpoints via: [http://localhost:8000/docs](http://localhost:8000/docs)

### 5. Run the Frontend (Streamlit)

```bash
cd ../frontend
streamlit run app.py
```

- This launches the UI at [http://localhost:8501](http://localhost:8501)

---

## 🔢 How It Works

1. User asks a question in the Streamlit UI.
2. The backend detects the intent (knowledge, geo, or retrieval).
3. Based on the route:
    - If **geo**, `geo_utils.py` parses keywords, returns coordinates & map.
    - If **kg**, `kg_interface.py` extracts entities and queries Neo4j.
    - If **rag**, `rag_pipeline.py` uses Gemini API with context snippets.
4. A formatted response is returned with optional:
    - Extracted triples
    - Source chunk
    - Confidence score
    - Map coordinates (Folium)

---

## 🕹️ Sample Queries

- “What is Oceansat-3 used for?”
- “Show me coverage of Gujarat”
- “Who launched INSAT-3D?”
- “Where is Kalpana-1 located?”

---

## 🚫 Troubleshooting

| Issue                  | Fix                                                        |
|------------------------|------------------------------------------------------------|
| ModuleNotFoundError    | Ensure you're in the correct venv and dependencies are installed |
| Neo4j Auth Failed      | Make sure `.env` contains correct `NEO4J_PASSWORD`         |
| Gemini API Error       | Validate API key and model name (e.g. gemini-pro, gemini-2.0-flash) |
| Streamlit Error        | Ensure correct port and Python path are used               |

---

## 📊 API Endpoints

| Endpoint | Method | Description                       |
|----------|--------|-----------------------------------|
| `/`      | GET    | Health check                      |
| `/ask`   | POST   | Main endpoint: `{ "question": "..." }` |
| `/query` | POST   | Alias for `/ask`                  |

---

## 👁‍🔍 Customization Guide

- **More question types?** Add new intent rules in `nlp_engine.py`
- **New data sources?** Extend `chunks.json` or integrate crawling
- **New map overlays?** Use `geo_utils.py` to inject more layers
- **Visual tweak?** Edit `frontend/app.py` layout and responses

---

## 📄 Requirements (from requirements.txt)

- fastapi
- uvicorn
- spacy
- neo4j
- python-dotenv
- requests
- google-generativeai
- streamlit
- folium
- streamlit-folium

---

## 🏆 Acknowledgments

- MOSDAC - ISRO for open access content
- Neo4j AuraDB for free-tier graph DB
- Google Gemini for LLM API
- spaCy and Streamlit for seamless UX

---

## 🚀 Status

SkyQuery AI Help Bot is currently under active development. Expect feature upgrades, improved RAG responses, and future support for multilingual queries and user feedback.

---

Made by Ishan, Vrushali & Soham