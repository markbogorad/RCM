import streamlit as st
import pandas as pd
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

# --- Whitelisted fields for coloring ---
YES_NO_COLUMNS = [
    'Dakota Select Lists', 'Dakota OCIO Business', 'Dakota Models',
    'Dakota Emerging Manager Program', 'Dakota Invests in Impact, SRI or ESG',
    'Dakota Hedge FOF', 'Dakota Real Estate FOF', 'Dakota Private Equity FOF',
    'Dakota Private Equity', 'Dakota Private Credit', 'Dakota Hedge Funds',
    'Dakota Private Real Estate', 'Dakota Liquid Alternatives',
    'Dakota Real Assets', 'Dakota Venture Capital'
]

ORDINAL_COLUMNS = {
    "Dakota Mutual Fund Usage", "Dakota LP Usage", "Dakota Separate Account Usage",
    "Dakota UMA Usage", "Dakota ETF Usage", "Dakota CIT Usage", "Dakota UCITS Usage"
}

NUMERIC_COLUMNS = ["Dakota AUM", "Score"]

def run_prospecting_page():
    st.subheader("📍 Prospecting Map & Scoring Tool")

    uploaded_file = st.file_uploader("📁 Upload Prospect Data (.csv)", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file, encoding='latin1')
    st.success(f"✅ Loaded {len(df)} records.")

    # --- Column detection ---
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    state_col = next((c for c in df.columns if "State" in c and "Dakota" in c), None)
    company_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    if not all([aum_col, state_col, company_col]):
        st.error("❌ Missing required fields: Dakota AUM, Dakota Billing State/Province, or Account Name.")
        st.stop()

    # --- Model scoring ---
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

    # --- MAP RENDERING ---
    st.markdown("### 🗺️ Map Visualization")

    valid_color_features = [
        col for col in df.columns if (
            col in YES_NO_COLUMNS or
            col in ORDINAL_COLUMNS or
            col in NUMERIC_COLUMNS
        )
    ]

    selected_overlay = st.selectbox("🎨 Color Bubbles By:", ["None"] + sorted(valid_color_features))
    color_feature = selected_overlay if selected_overlay != "None" else None

    try:
        st.plotly_chart(plot_mapbox_scatter(df, color_feature=color_feature), use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Could not render color overlay: {e}")
        st.plotly_chart(plot_mapbox_scatter(df), use_container_width=True)

    # --- Download scored file ---
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Scored Prospects", buffer, file_name="scored_prospects.csv")
