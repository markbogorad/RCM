import streamlit as st
import tempfile
import os
from agent_utils.open_source_agent import OpenSourceAgent

def run_ai_outreach_page():
    st.subheader("🤖 AI Outreach Agent")

    df = st.session_state.get("scored_prospect_df", None)
    if df is None:
        st.info("For full capacity, upload your data into the Prospecting tab. The agent will still respond, but without prospect data context.")

    # --- Setup agent with or without prospect data ---
    agent = OpenSourceAgent(
        system_message="You are an institutional sales strategist crafting targeted outreach messages based on prospect data.",
        data=df
    )

    # --- UI Chat Input ---
    user_input = st.chat_input("Ask the agent to craft a message...")

    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            try:
                response = agent.generate_response(user_input)
            except Exception as e:
                response = f"Error: {e}"
            st.markdown(response)
