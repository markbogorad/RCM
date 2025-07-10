import pandas as pd
import plotly.express as px
import streamlit as st
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import difflib
from prospect_utils.data_loader import clean_address_field, prepare_address_dataframe

# Set Mapbox token
px.set_mapbox_access_token(MAPBOX_TOKEN)

@st.cache_data(show_spinner=False)
def geocode_address(address):
    geolocator = Nominatim(user_agent="rcm_mapbox")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    try:
        loc = geocode(address)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return (None, None)

@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    df = prepare_address_dataframe(df)
    if df.empty or "Full_Address" not in df.columns:
        st.warning("⚠️ Address preparation failed or missing required columns.")
        return pd.DataFrame()

    coords = df["Full_Address"].apply(geocode_address)
    df["Latitude"] = coords.apply(lambda x: x[0])
    df["Longitude"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

def plot_mapbox_scatter(df, color_feature=None, state_filter=None, aum_filter=None, fund_filter=None, invest_filter=None):
    df = enrich_with_coordinates(df)
    if df.empty:
        st.warning("⚠️ Map could not be generated: no valid geocoded data.")
        return None

    def fuzzy_find(name):
        match = difflib.get_close_matches(name, df.columns, n=1, cutoff=0.7)
        return match[0] if match else None

    # Filter safely
    if state_filter:
        state_col = fuzzy_find("Dakota Billing State/Province")
        if state_col in df.columns:
            df = df[df[state_col] == state_filter]

    if aum_filter:
        aum_col = fuzzy_find("AUM Order")
        if aum_col in df.columns:
            df = df[df[aum_col] == aum_filter]

    if fund_filter:
        fund_col = fuzzy_find("Fund Usage")
        if fund_col in df.columns:
            df = df[df[fund_col] == fund_filter]

    if invest_filter:
        invest_col = fuzzy_find("Invests In")
        if invest_col in df.columns:
            df = df[df[invest_col] == invest_filter]

    if df.empty:
        st.warning("⚠️ No matching prospects after filters.")
        return None

    # Core columns
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    # --- Color Overlay ---
    color_type = "categorical"
    color_map = None

    if color_feature and color_feature in df.columns:
        col_values = df[color_feature].dropna().unique()
        if df[color_feature].dropna().isin(["Yes", "No", 1, 0]).all():
            color_type = "yesno"
            df[color_feature] = df[color_feature].replace({"Yes": 1, "No": 0})
            color_map = {0: "red", 1: "green"}
        elif df[color_feature].nunique() <= 4 and set(col_values).issubset({"Zero", "Small", "Medium", "Large"}):
            color_type = "ordinal"
            color_map = {"Zero": "lightgray", "Small": "red", "Medium": "orange", "Large": "green"}
        elif pd.api.types.is_numeric_dtype(df[color_feature]):
            color_type = "numeric"

    # --- Bubble Size ---
    size_col = None
    candidate_cols = ["Score", aum_col]
    for col in candidate_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if df[col].max() > 0:
                df = df[df[col] > 0]
                size_col = col
                break  # use first valid one

    if df.empty:
        st.warning("⚠️ No data with positive size for map bubbles.")
        return None

    # --- Build Map ---
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=color_feature if color_feature in df.columns else None,
        color_discrete_map=color_map if color_type in ["yesno", "ordinal", "categorical"] else None,
        color_continuous_scale="Viridis" if color_type == "numeric" else None,
        size=size_col,
        size_max=18,
        hover_name=name_col,
        hover_data=["Full_Address", aum_col, color_feature] if color_feature in df.columns else ["Full_Address", aum_col],
        zoom=3,
        center={"lat": 37.0902, "lon": -95.7129},  # USA center
        title=f"U.S. Prospects by {color_feature or 'Location'}"
    )

    fig.update_layout(
        mapbox_style="outdoors",
        margin=dict(l=0, r=0, t=30, b=0)
    )

    return fig
