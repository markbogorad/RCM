# pages/1_email_search_rank.py
import streamlit as st
from utils.email_scoring import extract_emails_and_context, score_email_contexts
import requests

st.set_page_config(page_title="Email Search & Rank", layout="wide")
st.title("🔍 Email Search & Semantic Scoring")

st.markdown("This tool extracts emails from a webpage and ranks them by semantic similarity to wealth management advisory language.")

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
