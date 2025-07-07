import pandas as pd
import plotly.express as px
import streamlit as st
import unicodedata
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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

# --- Clean any address field ---
def clean_address_field(val):
    if pd.isna(val):
        return ""
    val = str(val)
    val = unicodedata.normalize("NFKC", val)
    val = val.encode("ascii", "ignore").decode("utf-8")
    val = val.replace("\n", " ").replace("\r", " ")
    val = val.replace("’", "'").replace("“", '"').replace("”", '"')
    return val.strip()

# --- Normalize column header ---
def normalize_col(col):
    col = str(col)
    col = unicodedata.normalize("NFKC", col)
    col = col.encode("ascii", "ignore").decode("utf-8")
    col = col.replace("\xa0", " ").replace("\u200b", "")
    return col.strip()

# --- Match real dataset columns to expected field names ---
def get_column_mapping(df, expected_fields):
    cleaned_cols = {normalize_col(col): col for col in df.columns}
    mapping = {}
    for field in expected_fields:
        norm = normalize_col(field)
        match = cleaned_cols.get(norm)
        if not match:
            st.error(f"❌ Missing required column: `{field}`\n\nFound: {list(cleaned_cols.keys())}")
            raise KeyError(f"Missing required column: {field}")
        mapping[field] = match
    return mapping

# --- Enrich DataFrame with lat/lon coordinates ---
@st.cache_data(show_spinner=True)
def enrich_with_coordinates(df):
    if "Dakota Billing Country" in df.columns:
        df = df[df["Dakota Billing Country"].fillna("").str.upper() == "UNITED STATES"].copy()

    expected_fields = [
        "Dakota Billing Street",
        "Dakota Billing City",
        "Dakota Billing State/Province",
        "Dakota Billing Zip/Postal Code"
    ]

    col_map = get_column_mapping(df, expected_fields)
    street_col = col_map["Dakota Billing Street"]
    city_col = col_map["Dakota Billing City"]
    state_col = col_map["Dakota Billing State/Province"]
    zip_col = col_map["Dakota Billing Zip/Postal Code"]

    # Clean each address component
    for col in [street_col, city_col, state_col, zip_col]:
        df[col] = df[col].apply(clean_address_field)

    # Drop rows with any blank address component
    df = df.dropna(subset=[street_col, city_col, state_col, zip_col])
    df = df[df[[street_col, city_col, state_col, zip_col]].apply(lambda row: all(str(x).strip() for x in row), axis=1)].copy()

    # Build Full Address
    df["Full_Address"] = (
        df[street_col] + ", " +
        df[city_col] + ", " +
        df[state_col] + " " +
        df[zip_col].astype(str)
    )

    df = df[df["Full_Address"].str.len() > 10]
    st.write("📍 Sample addresses:", df["Full_Address"].sample(min(5, len(df))).tolist())

    # Geocode
    coords = df["Full_Address"].apply(geocode_address)
    df["Latitude"] = coords.apply(lambda x: x[0])
    df["Longitude"] = coords.apply(lambda x: x[1])
    df = df.dropna(subset=["Latitude", "Longitude"])

    return df

# --- Main Mapbox Plot ---
def plot_mapbox_scatter(df, color_feature=None):
    df = enrich_with_coordinates(df)

    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")

    if not color_feature or color_feature not in df.columns:
        color_feature = "Dakota Contact Type" if "Dakota Contact Type" in df.columns else None

    color_type = "categorical"
    color_map = None

    if color_feature in df.columns:
        values = df[color_feature].dropna().unique()

        if df[color_feature].dropna().isin(["Yes", "No", 1, 0]).all():
            color_type = "yesno"
            df[color_feature] = df[color_feature].replace({"Yes": 1, "No": 0})
            color_map = {0: "red", 1: "green"}
        elif df[color_feature].nunique() <= 4 and set(values).issubset({"Zero", "Small", "Medium", "Large"}):
            color_type = "ordinal"
            color_map = {"Zero": "lightgray", "Small": "red", "Medium": "orange", "Large": "green"}
        elif pd.api.types.is_numeric_dtype(df[color_feature]):
            color_type = "numeric"

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
