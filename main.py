# app.py
import streamlit as st
from utils.discovery_scraper import score_urls_from_query, get_clean_text
# from content_filter import extract_contacts  # Optional if defined

st.set_page_config(page_title="Wealth Research Scraper", layout="wide")
st.title("Wealth Management Research Web Scraper")

st.markdown("This app discovers and ranks websites using semantic relevance to research and advisory goals.")

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

        # Optional: Show contacts
        # contacts = extract_contacts(text)
        # if contacts:
        #     st.markdown(f"**📧 Contacts Found:** {contacts}")
