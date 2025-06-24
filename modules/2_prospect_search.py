import streamlit as st
import pandas as pd
import plotly.express as px
import io
import joblib

from prospect_utils.geo_utils import plot_us_map
from prospect_utils.score_utils import rule_based_score

# --- Load model + feature list ---
@st.cache_resource
def load_model():
    model = joblib.load("models/prospect_model.pkl")  # LightGBM or similar
    features = joblib.load("models/model_features.pkl")  # list of feature column names
    return model, features

def run_prospecting_page():
    st.subheader("📍 Prospecting Map & Scoring Tool")
    st.markdown("""
    Upload a CSV of prospect data to:
    
    - Visualize firms by state and metro
    - Score/rank them using:
        - A rule-based model (unsupervised)
        - A pre-trained tree model (supervised)

    **Required columns:** `Company`, `State`, `AUM`  
    **Optional columns:** `Metro`, `Strategy`, others used in model
    """)

    uploaded_file = st.file_uploader("📁 Upload Prospect Data (.csv)", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded {len(df)} records.")

    # Normalize/clean missing columns
    for col in ["State", "AUM"]:
        if col not in df.columns:
            st.error(f"Missing required column: `{col}`")
            st.stop()

    # Choose model type
    model_type = st.radio("Choose scoring model", ["🔧 Rule-based", "🌲 Pre-trained Tree Model"])

    if model_type == "🔧 Rule-based":
        df["Score"] = df.apply(rule_based_score, axis=1)
    else:
        model, model_features = load_model()
        missing = [f for f in model_features if f not in df.columns]
        if missing:
            st.error(f"Missing required features for model: {missing}")
            st.stop()

        X = df[model_features].copy()
        df["Score"] = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)

    df = df.sort_values("Score", ascending=False)
    st.dataframe(df[["Company", "State", "AUM", "Score"] + ([c for c in ["Metro"] if c in df.columns])])

    st.plotly_chart(plot_us_map(df), use_container_width=True)

    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Scored Prospects", buffer, file_name="scored_prospects.csv")
