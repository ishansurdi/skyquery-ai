# frontend/app.py

# import streamlit as st
# import requests

# st.set_page_config(page_title="SkyQuery AI Help Bot", page_icon="🛰️")

# st.title("🛰️ SkyQuery AI Help Bot")
# st.markdown("Ask me about satellite data, geospatial info, or anything from MOSDAC!")

# # Backend API URL
# API_URL = "http://localhost:8000/query"

# # Input box
# user_query = st.text_input("💬 Enter your question")

# if st.button("Ask") and user_query.strip():
#     with st.spinner("🧠 Thinking..."):
#         try:
#             response = requests.post(API_URL, json={"question": user_query})
#             if response.status_code == 200:
#                 result = response.json()
#                 st.success("✅ Answer")
#                 st.markdown(f"**Answer:** {result.get('answer', 'No answer')}")

#                 # Optional source, score, and triples
#                 if "source" in result:
#                     st.markdown(f"📄 **Source:** `{result['source']}`")
#                 if "confidence" in result:
#                     st.markdown(f"🔎 **Confidence:** {result['confidence']:.2f}")
#                 if "triples" in result and result["triples"]:
#                     st.markdown("🔗 **Extracted Triples:**")
#                     for s, r, o in result["triples"]:
#                         st.code(f"({s}) -[{r}]-> ({o})")

#             else:
#                 st.error("❌ Failed to get response from backend.")
#         except Exception as e:
#             st.error(f"🚨 Error: {e}")
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# --- Streamlit Page Config ---
st.set_page_config(page_title="MOSDAC AI Help Bot", page_icon="🛰️", layout="wide")

st.title("🛰️ SkyQuery AI Help Bot")
st.markdown("Ask me about satellite data, geospatial info, or anything from **[MOSDAC](https://www.mosdac.gov.in)**!")

# --- Sidebar ---
st.sidebar.title("📂 Quick Links")
st.sidebar.markdown("- 🛰️ Missions")
st.sidebar.markdown("- 📦 Products")
st.sidebar.markdown("- 📄 FAQs")
st.sidebar.markdown("- 📊 Documentation")

# --- Session State for Messages ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Show Message History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- API Endpoint ---
API_URL = "http://127.0.0.1:8000/ask"  # Make sure FastAPI is running on this endpoint

# --- Chat Input ---
if user_query := st.chat_input("💬 Ask me anything about MOSDAC..."):
    # Add user input to history
    st.session_state.messages.append({"role": "user", "content": user_query})

    with st.chat_message("user"):
        st.markdown(user_query)

    # API Request to Backend
    try:
        response = requests.post(API_URL, json={"question": user_query})
        if response.status_code == 200:
            result = response.json()
        else:
            st.error(f"❌ Backend Error: {response.status_code}")
            st.text(response.text)
            result = {}
    except Exception as e:
        st.error("🚨 Error connecting to backend!")
        st.text(str(e))
        result = {}

    # Extract answer and display
    answer = result.get("answer", "⚠️ No answer received.")
    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.markdown(answer)

    # Show extracted triples (if any)
    if triples := result.get("triples"):
        with st.expander("🔗 Extracted Triples"):
            for s, r, o in triples:
                st.code(f"({s}) -[{r}]-> ({o})")

    # Show source (optional)
    if source := result.get("source"):
        st.markdown(f"📄 **Source:** `{source}`")

    # Show confidence (optional)
    if conf := result.get("confidence"):
        st.markdown(f"🔍 **Confidence Score:** `{conf:.2f}`")

    # Show map (if location included)
    if "map_data" in result:
        map_data = result["map_data"]
        lat = map_data.get("lat", 20.5937)
        lon = map_data.get("lon", 78.9629)
        popup = map_data.get("popup", "Location Info")

        m = folium.Map(location=[lat, lon], zoom_start=5)
        folium.Marker([lat, lon], popup=popup).add_to(m)
        st.markdown("🗺️ **Relevant Map Location**")
        st_folium(m, width=700, height=500)
