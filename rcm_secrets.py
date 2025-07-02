import streamlit as st

MAPBOX_TOKEN = st.secrets["api_keys"]["mapbox"]
SERPAPI_KEY = st.secrets["api_keys"]["serpapi"]
MAX_RESULTS = st.secrets["api_keys"].get("max_results", 50)
