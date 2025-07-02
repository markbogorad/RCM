import pandas as pd
import plotly.express as px
import streamlit as st
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Initialize Mapbox
px.set_mapbox_access_token(MAPBOX_TOKEN)

# --- Caching for geocoding ---
@st.cache_data(show_spinner=False)
def geocode_address(address):
    geolocator = Nominatim(user_agent="rcm_mapbox")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    try:
        loc = geocode(address)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return (None, None)

# --- Address preprocessing + geocoding ---
@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    us_df = df[df["Dakota Billing Country"].fillna("").str.upper() == "UNITED STATES"].copy()

    # --- Build consistent full address using reliable fields only ---
    required_address_cols = [
        "Dakota Billing Street",
        "Dakota Billing City",
        "Dakota Billing State/Province",
        "Dakota Billing Zip/Postal Code"
    ]

    for col in required_address_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required address column: {col}")

        df["Full_Address"] = (
        df["Dakota Billing Street"].fillna("") + ", " +
        df["Dakota Billing City"].fillna("") + ", " +
        df["Dakota Billing State/Province"].fillna("") + " " +
        df["Dakota Billing Zip/Postal Code"].fillna("")
    )

        coords = us_df["Full_Address"].apply(geocode_address)
        us_df["Latitude"] = coords.apply(lambda x: x[0])
        us_df["Longitude"] = coords.apply(lambda x: x[1])
        us_df = us_df.dropna(subset=["Latitude", "Longitude"])

        return us_df

# --- Main plotting function ---
def plot_mapbox_scatter(df, color_feature=None):
    df = enrich_with_coordinates(df)

    # --- Detect label columns ---
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    # --- Determine color type ---
    if not color_feature or color_feature not in df.columns:
        color_feature = "Dakota Contact Type" if "Dakota Contact Type" in df.columns else None

    color_type = "categorical"
    if color_feature in df.columns:
        unique_vals = df[color_feature].dropna().unique()
        if df[color_feature].dropna().isin(["Yes", "No", 1, 0]).all():
            color_type = "yesno"
            df[color_feature] = df[color_feature].replace({"Yes": 1, "No": 0})
            color_map = {0: "red", 1: "green"}
        elif df[color_feature].nunique() <= 4 and set(unique_vals).issubset({"Zero", "Small", "Medium", "Large"}):
            color_type = "ordinal"
            color_map = {"Zero": "lightgray", "Small": "red", "Medium": "orange", "Large": "green"}
        elif pd.api.types.is_numeric_dtype(df[color_feature]):
            color_type = "numeric"
            color_map = None
        else:
            color_map = None
    else:
        color_type = None
        color_map = None

    # --- Build plot ---
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=color_feature if color_type else None,
        color_discrete_map=color_map if color_type in ["yesno", "ordinal", "categorical"] else None,
        color_continuous_scale="Viridis" if color_type == "numeric" else None,
        size="Score" if "Score" in df.columns else aum_col,
        size_max=18,
        zoom=3,
        hover_name=name_col,
        hover_data=["Full_Address", aum_col, color_feature] if color_feature else ["Full_Address", aum_col],
        title=f"U.S. Prospects by {color_feature or 'Location'}"
    )
    fig.update_layout(mapbox_style="streets", margin=dict(l=0, r=0, t=30, b=0))
    return fig
