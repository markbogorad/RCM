import pandas as pd
import plotly.express as px
import streamlit as st
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import difflib

# Set Mapbox token
px.set_mapbox_access_token(MAPBOX_TOKEN)

# --- Geocoding ---
@st.cache_data(show_spinner=False)
def geocode_address(address):
    geolocator = Nominatim(user_agent="rcm_mapbox")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    try:
        loc = geocode(address)
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return (None, None)

# --- Clean address fields ---
def clean_address_field(val):
    if pd.isna(val):
        return ""
    val = str(val).encode("ascii", "ignore").decode("utf-8")
    val = val.replace("\n", " ").replace("\r", " ")
    val = val.replace("’", "'").replace("“", '"').replace("”", '"')
    return val.strip()

# --- Coordinate enrichment ---
@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ")
        .str.replace(" +", " ", regex=True)
    )

    # Fuzzy match required fields
    required_fields = {
        "Dakota Billing Street": None,
        "Dakota Billing City": None,
        "Dakota Billing State/Province": None,
        "Dakota Billing Zip/Postal Code": None
    }

    for key in required_fields:
        match = difflib.get_close_matches(key, df.columns, n=1, cutoff=0.8)
        if match:
            required_fields[key] = match[0]
        else:
            st.warning(f"⚠️ Missing required column: {key}")
            return pd.DataFrame()

    street_col = required_fields["Dakota Billing Street"]
    city_col = required_fields["Dakota Billing City"]
    state_col = required_fields["Dakota Billing State/Province"]
    zip_col = required_fields["Dakota Billing Zip/Postal Code"]

    # Filter to U.S. only
    country_col = next((c for c in df.columns if "Country" in c), None)
    if country_col:
        df = df[df[country_col].fillna("").str.upper() == "UNITED STATES"].copy()

    # Clean and validate address fields
    df = df.dropna(subset=[street_col, city_col, state_col, zip_col])
    for col in [street_col, city_col, state_col, zip_col]:
        df[col] = df[col].apply(clean_address_field)

    df = df[
        df[[street_col, city_col, state_col, zip_col]].apply(lambda row: all(str(x).strip() for x in row), axis=1)
    ].copy()

    # Construct full address
    try:
        df["Full_Address"] = (
            df[street_col] + ", " +
            df[city_col] + ", " +
            df[state_col] + " " +
            df[zip_col].astype(str)
        )
    except Exception as e:
        st.warning(f"⚠️ Address formatting failed: {e}")
        return pd.DataFrame()

    df = df[df["Full_Address"].str.len() > 10]

    # Geocode
    coords = df["Full_Address"].apply(geocode_address)
    df["Latitude"] = coords.apply(lambda x: x[0])
    df["Longitude"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["Latitude", "Longitude"])

    return df

# --- Map rendering ---
def plot_mapbox_scatter(df, color_feature=None):
    df = enrich_with_coordinates(df)
    if df.empty:
        st.warning("⚠️ Map could not be generated: no valid geocoded data.")
        return None

    # Basic columns
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    # Color overlay logic
    if not color_feature or color_feature not in df.columns:
        color_feature = "Dakota Contact Type" if "Dakota Contact Type" in df.columns else None

    color_type = "categorical"
    color_map = None

    if color_feature in df.columns:
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
        else:
            color_type = "categorical"

    # --- Size handling ---
    size_col = "Score" if "Score" in df.columns else aum_col
    if size_col and size_col in df.columns:
        df[size_col] = pd.to_numeric(df[size_col], errors="coerce")
        df = df[df[size_col] > 0].copy()
    else:
        size_col = None

    # Plot
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=color_feature if color_type else None,
        color_discrete_map=color_map if color_type in ["yesno", "ordinal", "categorical"] else None,
        color_continuous_scale="Viridis" if color_type == "numeric" else None,
        size=size_col,
        size_max=18,
        zoom=3,
        hover_name=name_col,
        hover_data=["Full_Address", aum_col, color_feature] if color_feature else ["Full_Address", aum_col],
        title=f"U.S. Prospects by {color_feature or 'Location'}"
    )
    fig.update_layout(mapbox_style="streets", margin=dict(l=0, r=0, t=30, b=0))
    return fig
