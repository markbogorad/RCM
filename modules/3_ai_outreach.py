import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from agentbase import Agent, AgentStream
import tempfile
import os

def run_ai_outreach_page():
    st.subheader("🤖 AI Outreach Agent")

    if "scored_prospect_df" not in st.session_state:
        st.error("❌ No prospect data found. Please upload and score data in the Prospecting tab first.")
        return

    df = st.session_state["scored_prospect_df"]

    # --- Convert dataframe to a text file for RAG ---
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "prospects.csv")
        df.to_csv(csv_path, index=False)

        docs = SimpleDirectoryReader(tmpdir).load_data()
        index = VectorStoreIndex.from_documents(docs)

        # --- Setup agent with retrieval tool ---
        agent = Agent(
            system_message="You are an institutional sales strategist crafting targeted outreach messages based on prospect data.",
            tools=[index.as_query_engine()],
        )

        # --- UI Chat Input ---
        user_input = st.chat_input("Ask the agent to craft a message...")

        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                stream = AgentStream(agent, user_input)
                stream.stream_to_streamlit()
