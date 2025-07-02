import pandas as pd
import plotly.express as px
import streamlit as st
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Set Mapbox token once
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

# --- Clean individual address fields ---
def clean_address_field(val):
    if pd.isna(val):
        return ""
    val = str(val).encode("ascii", "ignore").decode("utf-8")
    val = val.replace("\n", " ").replace("\r", " ")
    val = val.replace("’", "'").replace("“", '"').replace("”", '"')
    return val.strip()

# --- Enrich with lat/lon ---
@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.replace('\xa0', ' ')
        .str.replace(' +', ' ', regex=True)
    )

    # Print for debugging
    print("Available columns:", df.columns.tolist())

    # Filter to U.S. only
    if "Dakota Billing Country" in df.columns:
        df = df[df["Dakota Billing Country"].fillna("").str.upper() == "UNITED STATES"].copy()

    # Required address fields
    required_fields = [
        "Dakota Billing Street",
        "Dakota Billing City",
        "Dakota Billing State/Province",
        "Dakota Billing Zip/Postal Code"
    ]

    missing = [col for col in required_fields if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required address columns: {missing}")

    # Drop rows with missing parts
    df = df.dropna(subset=required_fields)
    for col in required_fields:
        df[col] = df[col].apply(clean_address_field)

    df = df[df[required_fields].apply(lambda row: all(str(x).strip() for x in row), axis=1)].copy()

    # Build full address
    df["Full_Address"] = (
        df["Dakota Billing Street"].str.strip() + ", " +
        df["Dakota Billing City"].str.strip() + ", " +
        df["Dakota Billing State/Province"].str.strip() + " " +
        df["Dakota Billing Zip/Postal Code"].astype(str).str.strip()
    )

    # Drop any remaining bad addresses
    df = df[df["Full_Address"].str.len() > 10]

    # Geocode
    coords = df["Full_Address"].apply(geocode_address)
    df["Latitude"] = coords.apply(lambda x: x[0])
    df["Longitude"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["Latitude", "Longitude"])

    return df

# --- Main Mapbox scatter plot function ---
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

    # Plot
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
