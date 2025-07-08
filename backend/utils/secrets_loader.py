import os
from dotenv import load_dotenv

try:
    import streamlit as st
    IN_STREAMLIT = True
except ImportError:
    IN_STREAMLIT = False

load_dotenv()  # always load .env regardless

def get_secret(key: str, default=None):
    if IN_STREAMLIT and hasattr(st, "secrets"):
        try:
            return st.secrets.get(key, default)
        except Exception:
            pass  # fallback to .env
    return os.getenv(key, default)
