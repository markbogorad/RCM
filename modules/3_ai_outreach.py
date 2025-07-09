import streamlit as st

def run_ai_outreach_page():
    st.subheader("🤖 AI Outreach Agent")
    st.warning("Embedding is restricted by Microsoft, so this tool must be opened in a new tab.")

    st.markdown(
        """
        <a href="https://m365.cloud.microsoft/chat/?fromCode=cmcv2&redirectId=C1DD6574EC0244BA9C1C8025AC74C510&auth=2"
           target="_blank"
           style="display:inline-block;padding:12px 24px;background:#0078d4;color:white;border-radius:6px;text-decoration:none;">
            🔗 Open AI Agent in Microsoft Cloud
        </a>
        """,
        unsafe_allow_html=True
    )
