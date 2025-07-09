import streamlit as st

def run_ai_outreach_page():
    st.subheader("🤖 AI Outreach Agent")
    st.markdown("This tool embeds the AI agent interface below. Please wait a moment if it takes time to load.")

    # Replace this with your actual agent's URL
    agent_url = "https://m365.cloud.microsoft/chat/?fromCode=cmcv2&redirectId=C1DD6574EC0244BA9C1C8025AC74C510&auth=2"

    # Embed via iframe
    st.components.v1.html(
        f"""
        <iframe src="{agent_url}" width="100%" height="800px" frameborder="0" allowfullscreen></iframe>
        """,
        height=820,
    )
