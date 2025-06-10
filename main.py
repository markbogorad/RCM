# main.py (only file needed)
import streamlit as st
from utils.discovery_scraper import score_urls_from_query, get_clean_text
from utils.email_scoring import extract_emails_and_context, score_email_contexts
import requests

st.set_page_config(page_title="Wealth Research Toolkit", layout="wide")

st.markdown("<h1 style='text-align: center;'>🏛️ Wealth Management Research Toolkit</h1>", unsafe_allow_html=True)
st.markdown("")

# Clean horizontal tabs
tabs = st.tabs(["🔍 Discovery", "📧 Email Scorer", "📍 Location Query"])

# --- Discovery Tab ---
with tabs[0]:
    st.subheader("🔍 Website Semantic Discovery")
    query = st.text_input("Enter a search query", value="top wealth management firms 2024")
    if st.button("Run Discovery"):
        with st.spinner("Running semantic discovery..."):
            results = score_urls_from_query(query)

        st.success(f"Found and scored {len(results)} pages.")
        for i, (url, score) in enumerate(results):
            st.markdown(f"### {i+1}. [{url}]({url})")
            st.markdown(f"**Semantic Score:** `{score:.4f}`")
            with st.expander("📝 Preview Text Snippet", expanded=False):
                text = get_clean_text(url)
                st.write(text[:1000] + "..." if len(text) > 1000 else text)

# --- Email Tab ---
with tabs[1]:
    st.subheader("📧 Semantic Email Extractor")
    url = st.text_input("Enter the URL to analyze", value="https://www.stifel.com")
    if st.button("Scan Page for Emails"):
        try:
            with st.spinner("Fetching page content..."):
                html = requests.get(url, timeout=10).text
            with st.spinner("Extracting emails and scoring..."):
                raw_emails = extract_emails_and_context(html)
                scored_emails = score_email_contexts(raw_emails)
            if scored_emails:
                st.success(f"Found {len(scored_emails)} emails.")
                for i, (email, context, score) in enumerate(scored_emails):
                    st.markdown(f"### {i+1}. {email}")
                    st.markdown(f"**Score:** `{score:.4f}`")
                    with st.expander("📝 Context", expanded=False):
                        st.write(context)
            else:
                st.warning("No emails found.")
        except Exception as e:
            st.error(f"Failed to process URL: {e}")

# --- Location Tab ---
with tabs[2]:
    st.subheader("📍 Location-Based Query (Coming Soon)")
    st.info("This module will allow geographic filtering and search refinement by city or firm HQ.")
