import streamlit as st
import importlib.util
import sys
import toml
from rcm_secrets import MAPBOX_TOKEN, SERPAPI_KEY, MAX_RESULTS


# --- Dynamic Module Loader ---
def load_module_as(name, filepath):
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# --- Load Pages ---
email_search_page = load_module_as("email_search_rank", "modules/1_email_search_rank.py")
prospecting_page = load_module_as("prospecting_map", "modules/2_prospect_search.py")

# --- Streamlit App Config ---
st.set_page_config(page_title="Wealth Research Toolkit", layout="wide")

st.markdown("<h1 style='text-align: center;'>🏛️ RAM Sales Research Toolkit</h1>", unsafe_allow_html=True)
st.markdown("")

# --- Top-Level Tabs ---
tabs = st.tabs(["📧 Email Search", "📍 Prospecting", "AI Outreach (Coming Soon)"])

with tabs[0]:
    email_search_page.run_email_rank_page()

with tabs[1]:
    prospecting_page.run_prospecting_page()

with tabs[2]:
    st.subheader("AI Outreach (Coming Soon)")
    st.info("More tools coming soon.")
