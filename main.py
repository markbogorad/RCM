import streamlit as st
import importlib.util
import sys

# --- Load module with non-standard filename ---
def load_module_as(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

email_search_page = load_module_as("email_search_rank", "modules/1_email_search_rank.py")

# --- Streamlit config ---
st.set_page_config(page_title="Wealth Research Toolkit", layout="wide")

st.markdown("<h1 style='text-align: center;'>🏛️ RAM Sales Research Toolkit</h1>", unsafe_allow_html=True)
st.markdown("")

# --- Top-level tabs ---
tabs = st.tabs(["📧 Email Search", "📍 Prospecting", " Coming Soon "])

# --- Email Search Tab ---
with tabs[0]:
    email_search_page.run_email_rank_page()

# --- Discovery Tab ---
with tabs[1]:
    st.subheader("🔍 Prospecting")
    query = st.text_input("Enter a search query", value="top wealth management firms 2024")

# --- Location Tab ---
with tabs[2]:
    st.subheader("📍 Location-Based Query (Coming Soon)")
    st.info("This module will allow geographic filtering and search refinement by city or firm HQ.")
