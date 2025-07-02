import streamlit as st
import pandas as pd
import plotly.express as px
import io
import joblib

from prospect_utils.geo_utils import plot_mapbox_scatter
from prospect_utils.score_utils import rule_based_score

# --- Load model + feature list ---
@st.cache_resource
def load_model():
    model = joblib.load("models/prospect_model.pkl")
    features = joblib.load("models/model_features.pkl")
    return model, features

def run_prospecting_page():
    st.subheader("📍 Prospecting Map & Scoring Tool")
    st.markdown("""
    Upload a CSV of prospect data to:

    - Visualize firms as points on a U.S. Mapbox map
    - Score/rank them using:
        - A rule-based model (unsupervised)
        - A pre-trained tree model (supervised)

    **Required fields:** Billing address columns (Street, City, State, Zip), `Dakota AUM`  
    """)

    # --- Upload data ---
    uploaded_file = st.file_uploader("📁 Upload Prospect Data (.csv)", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file, encoding='latin1')
    st.success(f"✅ Loaded {len(df)} records.")

    # --- Auto-detect key columns ---
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    state_col = next((c for c in df.columns if "State" in c and "Dakota" in c), None)
    company_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")
    metro_col = next((c for c in df.columns if "Metro" in c), None)

    if not all([aum_col, state_col, company_col]):
        st.error("❌ Missing required fields: Dakota AUM, Dakota Billing State/Province, or Account Name.")
        st.stop()

    # --- Scoring Model Selection ---
    model_type = st.radio("🧠 Choose scoring model", ["🔧 Rule-based", "🌲 Tree-based Model"])

    if model_type == "🔧 Rule-based":
        df["Score"] = df.apply(rule_based_score, axis=1)
    else:
        model, model_features = load_model()
        missing = [f for f in model_features if f not in df.columns]
        if missing:
            st.error(f"❌ Missing required model features: {missing}")
            st.stop()

        X = df[model_features].copy()
        df["Score"] = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else model.predict(X)

    # --- Preview Table ---
    df = df.sort_values("Score", ascending=False)
    display_cols = [company_col, state_col, aum_col, "Score"]
    if metro_col:
        display_cols.append(metro_col)
    st.dataframe(df[display_cols])

    # --- Map Feature Selection ---
    st.markdown("### 🗺️ Map Customization")
    feature_options = [col for col in df.columns if df[col].nunique() > 1 and df[col].nunique() < 100]
    color_feature = st.selectbox("🎨 Color code map by:", options=feature_options, index=0)

    # --- Map Rendering ---
    st.plotly_chart(plot_mapbox_scatter(df, color_feature=color_feature), use_container_width=True)

    # --- Download Button ---
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Scored Prospects", buffer, file_name="scored_prospects.csv")
