import streamlit as st
import tempfile
import os
from agent_utils.open_source_agent import OpenSourceAgent

def run_ai_outreach_page():
    st.subheader("🤖 AI Outreach Agent")

    if "scored_prospect_df" not in st.session_state:
        st.error("❌ No prospect data found. Please upload and score data in the Prospecting tab first.")
        return

    df = st.session_state["scored_prospect_df"]

    # --- Setup agent with prospect data ---
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
            response = agent.generate_response(user_input)
            st.markdown(response)
