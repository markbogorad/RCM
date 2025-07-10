import streamlit as st
import pandas as pd
import io
import time

from email_utils.semantic_utils import get_reference_embeddings
from email_utils.scoring_utils import score_candidates, summarize_hits
from email_utils.analytics_utils import compute_word_frequencies, render_summary_table
from email_utils.scraper_utils import (
    run_reverse_search,
    fetch_html_from_url,
    extract_named_snippets,
    extract_all_emails,
    match_username_to_name,
)

def run_email_discovery(first, last, company, title=None):
    name = f"{first} {last}"
    search_results = run_reverse_search(first, last, company, title=title, max_results=7)

    all_candidates = []
    all_context_blocks = []

    for result in search_results:
        url = result.get("link")
        if not url:
            continue

        html = fetch_html_from_url(url)
        if not html:
            continue

        snippets = extract_named_snippets(html, name)
        all_context_blocks.extend(snippets)

        found_emails = extract_all_emails(html)
        for email in found_emails:
            username = email.split("@")[0]
            if match_username_to_name(username, first, last):
                context = next((s for s in snippets if username in s), snippets[0] if snippets else "")
                all_candidates.append((email, context))

    reference_embeddings = get_reference_embeddings()
    scored = score_candidates(all_candidates, reference_embeddings)
    summary = summarize_hits(scored)
    word_freq = compute_word_frequencies(all_context_blocks)

    return scored, summary, word_freq

def run_email_rank_page():
    st.subheader("📧 Email Search & Semantic Scoring")

    st.markdown("""
    This tool searches for and ranks potential emails for financial professionals using a blend of name-based search,
    semantic scoring, and pattern generation. The more details you provide, the better the results.
    
    **Required fields:** First Name, Last Name, Company.
    **Special characters must be excluded**
    """)

    with st.form("search_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            first_name = st.text_input("First Name*", placeholder="John")
            company = st.text_input("Company*", placeholder="Goldman Sachs")
            phone = st.text_input("Phone", placeholder="Optional")

        with col2:
            last_name = st.text_input("Last Name*", placeholder="Smith")
            street = st.text_input("Street", placeholder="Optional")

        with col3:
            title = st.text_input("Title", placeholder="Portfolio Manager")
            city = st.text_input("City", placeholder="Optional")
            state = st.text_input("State", placeholder="Optional")
            zip_code = st.text_input("Zip", placeholder="Optional")
            country = st.text_input("Country", placeholder="Optional")
            crd = st.text_input("CRD#", placeholder="Optional")

        submitted = st.form_submit_button("🔍 Search for Emails")

    if submitted:
        if not first_name or not last_name or not company:
            st.error("⚠️ Please provide at least First Name, Last Name, and Company.")
        else:
            with st.spinner("Running search, scraping pages, scoring candidates..."):
                start = time.time()
                results, summary, word_freq = run_email_discovery(
                    first_name, last_name, company, title=title
                )
                st.success(f"Search complete in {round(time.time() - start, 1)} seconds.")

            st.markdown("### 📧 Ranked Emails")
            if results:
                for i, (email, context, score) in enumerate(results):
                    st.markdown(f"**{i+1}. `{email}`** — Score: `{score:.4f}`")
                    with st.expander("📝 Context Snippet"):
                        st.write(context)
            else:
                st.warning("No emails found.")

            st.markdown("### 📊 Summary")
            render_summary_table(st, summary)

            st.markdown("### 🔠 Most Common Words")
            for word, count in word_freq:
                st.markdown(f"- **{word}** ({count})")

    # --- CSV Upload Section ---
    st.markdown("---")
    st.subheader("📁 Batch Upload (CSV)")

    # Download Template Button
    st.markdown("### 📄 Download CSV Template")
    template_headers = [
        "First Name", "Last Name", "Company", "Title", "Phone Number",
        "Street", "City", "State", "Zip", "Country", "CRD#"
    ]
    template_df = pd.DataFrame(columns=template_headers)
    buffer = io.BytesIO()
    template_df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 Download Template CSV",
        data=buffer,
        file_name="email_search_template.csv",
        mime="text/csv"
    )

    # Upload Area
    uploaded_file = st.file_uploader("Upload CSV with at least: First Name, Last Name, Company", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        required_cols = {"First Name", "Last Name", "Company"}

        if not required_cols.issubset(df.columns):
            st.error("CSV must contain at least: First Name, Last Name, Company.")
        else:
            st.success(f"Found {len(df)} rows. Starting batch search...")

            found_emails = []
            for i, row in df.iterrows():
                st.markdown(f"### 🔎 {i+1}. {row['First Name']} {row['Last Name']} ({row['Company']})")
                with st.spinner("Scanning..."):
                    results, summary, word_freq = run_email_discovery(
                        row["First Name"], row["Last Name"], row["Company"], title=row.get("Title", None)
                    )
                if results:
                    best_email, _, best_score = results[0]
                    st.markdown(f"**Top Email:** `{best_email}` — Score: `{best_score:.4f}`")
                    found_emails.append(best_email)
                else:
                    st.warning("No email found.")
                    found_emails.append("")

            # Add found emails to DataFrame
            df["Found Email"] = found_emails

            # Download buttons for CSV and Excel
            st.markdown("### 📤 Download Results")
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv_buffer,
                file_name="email_search_results.csv",
                mime="text/csv"
            )

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False)
            excel_buffer.seek(0)
            st.download_button(
                label="📥 Download Results as Excel",
                data=excel_buffer,
                file_name="email_search_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
