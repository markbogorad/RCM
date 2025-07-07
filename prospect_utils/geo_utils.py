import pandas as pd
import plotly.express as px
import streamlit as st
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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

def clean_address_field(val):
    if pd.isna(val):
        return ""
    val = str(val).encode("ascii", "ignore").decode("utf-8")
    val = val.replace("\n", " ").replace("\r", " ")
    val = val.replace("’", "'").replace("“", '"').replace("”", '"')
    return val.strip()

@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ")
        .str.replace(" +", " ", regex=True)
    )

    # Map cleaned names to actual names
    normalized_map = {col.strip().replace("\xa0", " ").replace("  ", " "): col for col in df.columns}

    required = [
        "Dakota Billing Street",
        "Dakota Billing City",
        "Dakota Billing State/Province",
        "Dakota Billing Zip/Postal Code"
    ]

    missing = [col for col in required if col not in normalized_map]
    if missing:
        raise KeyError(f"Missing required address columns: {missing}\nAvailable columns: {list(df.columns)}")

    # Map to real internal names
    street_col = normalized_map["Dakota Billing Street"]
    city_col = normalized_map["Dakota Billing City"]
    state_col = normalized_map["Dakota Billing State/Province"]
    zip_col = normalized_map["Dakota Billing Zip/Postal Code"]

    # U.S. only
    if "Dakota Billing Country" in df.columns:
        df = df[df["Dakota Billing Country"].fillna("").str.upper() == "UNITED STATES"].copy()

    # Drop incomplete rows
    df = df.dropna(subset=[street_col, city_col, state_col, zip_col])
    for col in [street_col, city_col, state_col, zip_col]:
        df[col] = df[col].apply(clean_address_field)
    df = df[
        df[[street_col, city_col, state_col, zip_col]].apply(lambda row: all(str(x).strip() for x in row), axis=1)
    ].copy()

    # Build Full_Address using real column names
    df["Full_Address"] = (
        df[street_col] + ", " +
        df[city_col] + ", " +
        df[state_col] + " " +
        df[zip_col].astype(str)
    )
    df = df[df["Full_Address"].str.len() > 10]

    coords = df["Full_Address"].apply(geocode_address)
    df["Latitude"] = coords.apply(lambda x: x[0])
    df["Longitude"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["Latitude", "Longitude"])

    return df

def plot_mapbox_scatter(df, color_feature=None):
    df = enrich_with_coordinates(df)

    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

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
