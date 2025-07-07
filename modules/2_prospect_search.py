import streamlit as st
import pandas as pd
import io
import joblib

from prospect_utils.geo_utils import plot_mapbox_scatter
from prospect_utils.score_utils import rule_based_score

@st.cache_resource
def load_model():
    model = joblib.load("models/prospect_model.pkl")
    features = joblib.load("models/model_features.pkl")
    return model, features

# --- Whitelisted overlay fields for strategic filtering ---
AUM_ORDER_COL = "AUM Order"

FUND_USAGE_OPTIONS = [
    "Dakota Hedge Funds", "Dakota Private Credit", "Dakota Private Equity",
    "Dakota Private Real Estate", "Dakota Real Assets", "Dakota Venture Capital"
]

INVESTMENT_TAGS = [
    "Dakota Invests in Impact, SRI or ESG",
    "Dakota Select Lists", "Dakota OCIO Business", "Dakota Models"
]

def run_prospecting_page():
    st.subheader("📍 Prospecting Map & Scoring Tool")

    uploaded_file = st.file_uploader("📁 Upload Prospect Data (.csv)", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file, encoding='latin1')
    st.success(f"✅ Loaded {len(df)} records.")

    # --- Column checks ---
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    state_col = next((c for c in df.columns if "State" in c and "Dakota" in c), None)
    company_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    if not all([aum_col, state_col, company_col]):
        st.error("❌ Missing required fields: Dakota AUM, Dakota Billing State/Province, or Account Name.")
        st.stop()

    # --- Scoring ---
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

    # --- Attribute filtering & coloring ---
    st.markdown("### 🎯 Filter & Color by Strategy")

    aum_order = None
    fund_usage = None
    invests_in = None
    overlay_field = None

    with st.expander("Filter by:", expanded=True):
        if AUM_ORDER_COL in df.columns:
            aum_order = st.selectbox("• AUM Order", options=[""] + sorted(df[AUM_ORDER_COL].dropna().unique().tolist()))

        available_funds = [col for col in FUND_USAGE_OPTIONS if col in df.columns]
        if available_funds:
            fund_usage = st.selectbox("• Fund Usage", options=[""] + available_funds)

        available_invests = [col for col in INVESTMENT_TAGS if col in df.columns]
        if available_invests:
            invests_in = st.selectbox("• Invests In", options=[""] + available_invests)

    # --- Color overlay determined by user filter ---
    overlay_field = fund_usage or invests_in or None

    # --- Plot map ---
    try:
        st.plotly_chart(
            plot_mapbox_scatter(
                df,
                color_feature=overlay_field,
                aum_filter=aum_order,
                fund_filter=fund_usage,
                invest_filter=invests_in
            ),
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"⚠️ Could not render map: {e}")

    # --- Download scored results ---
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Scored Prospects", buffer, file_name="scored_prospects.csv")
