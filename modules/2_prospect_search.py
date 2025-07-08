import streamlit as st
import pandas as pd
import io
import joblib
import difflib

from prospect_utils.geo_utils import plot_mapbox_scatter
from prospect_utils.score_utils import rule_based_score

@st.cache_resource
def load_model():
    model = joblib.load("models/prospect_model.pkl")
    features = joblib.load("models/model_features.pkl")
    return model, features

# --- Strategy filtering definitions ---
AUM_ORDER_TARGET = "AUM Order"
FUND_USAGE_COLUMNS = [
    "Dakota Hedge Funds", "Dakota Private Credit", "Dakota Private Equity",
    "Dakota Private Real Estate", "Dakota Real Assets", "Dakota Venture Capital"
]
INVEST_TAG_COLUMNS = [
    "Dakota Invests in Impact, SRI or ESG",
    "Dakota Select Lists", "Dakota OCIO Business", "Dakota Models"
]

# --- Utility to fuzzy match a column name ---
def fuzzy_match(colname, df_cols):
    match = difflib.get_close_matches(colname, df_cols, n=1, cutoff=0.7)
    return match[0] if match else None

# --- Main page logic ---
def run_prospecting_page():
    st.subheader("📍 Prospecting Map & Scoring Tool")

    uploaded_file = st.file_uploader("📁 Upload Prospect Data (.csv)", type=["csv"])
    if not uploaded_file:
        st.stop()

    df = pd.read_csv(uploaded_file, encoding='latin1')
    st.success(f"✅ Loaded {len(df)} records.")

    # --- Required columns ---
    df_cols = df.columns.tolist()
    aum_col = fuzzy_match("Dakota AUM", df_cols)
    state_col = fuzzy_match("Dakota Billing State/Province", df_cols)
    company_col = fuzzy_match("Dakota Account Name", df_cols) or "Provided Account Name"

    if not all([aum_col, state_col, company_col]):
        st.error("❌ Required fields not found: Dakota AUM, Billing State, or Account Name.")
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

    # --- Filters ---
    st.markdown("### 🎯 Filter & Color by Strategy")

    aum_order_filter = None
    fund_usage_filter = None
    invests_in_filter = None
    overlay_field = None

    with st.expander("Filter by:", expanded=True):
        # AUM Order dropdown
        aum_order_col = fuzzy_match(AUM_ORDER_TARGET, df.columns)
        if aum_order_col:
            aum_order_vals = df[aum_order_col].dropna().unique().tolist()
            aum_order_filter = st.selectbox("• AUM Order", [""] + sorted(aum_order_vals))

        # Fund usage dropdown (show column names)
        available_funds = [col for col in FUND_USAGE_COLUMNS if col in df.columns]
        if available_funds:
            fund_usage_filter = st.selectbox("• Fund Usage", [""] + available_funds)

        # Invests in dropdown (show column names)
        available_invests = [col for col in INVEST_TAG_COLUMNS if col in df.columns]
        if available_invests:
            invests_in_filter = st.selectbox("• Invests In", [""] + available_invests)

    # Determine color overlay
    overlay_field = fund_usage_filter or invests_in_filter or None

    # --- Render Map ---
    try:
        st.plotly_chart(
            plot_mapbox_scatter(
                df,
                color_feature=overlay_field,
                aum_filter=aum_order_filter if aum_order_filter else None,
                fund_filter=fund_usage_filter if fund_usage_filter else None,
                invest_filter=invests_in_filter if invests_in_filter else None
            ),
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"⚠️ Could not render map: {e}")

    # --- Download scored file ---
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Scored Prospects", buffer, file_name="scored_prospects.csv")
