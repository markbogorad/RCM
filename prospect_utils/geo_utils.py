import plotly.express as px
import pandas as pd
from rcm_secrets import MAPBOX_TOKEN
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Set token once
px.set_mapbox_access_token(MAPBOX_TOKEN)

def geocode_addresses(df, address_col="Full_Address"):
    """Add Latitude and Longitude columns to the DataFrame."""
    geolocator = Nominatim(user_agent="rcm_mapbox")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    df["Location"] = df[address_col].apply(geocode)
    df["Latitude"] = df["Location"].apply(lambda loc: loc.latitude if loc else None)
    df["Longitude"] = df["Location"].apply(lambda loc: loc.longitude if loc else None)
    return df.drop(columns=["Location"])

def plot_mapbox_scatter(df):
    """
    Plots prospects as points on a Mapbox map.
    Color = Contact Type or Platform
    Size = Dakota AUM or Score
    Hover = Account Name, Location, AUM
    """

    # --- Build full address if needed ---
    addr_fields = [
        "Dakota Billing Street", 
        "Dakota Billing City", 
        "Dakota Billing State/Province", 
        "Dakota Billing Zip/Postal Code"
    ]
    available_fields = [f for f in addr_fields if f in df.columns]
    df["Full_Address"] = df[available_fields].fillna("").agg(", ".join, axis=1)

    # --- Geocode if missing lat/lon ---
    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        df = geocode_addresses(df)

    # --- Column detection ---
    aum_col = next((c for c in df.columns if "Dakota AUM" in c), None)
    name_col = next((c for c in df.columns if "Account Name" in c and "Dakota" in c), "Provided Account Name")
    type_col = next((c for c in df.columns if "Contact Type" in c), None)

    # --- Plot ---
    fig = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color=type_col,
        size="Score" if "Score" in df.columns else aum_col,
        size_max=20,
        zoom=3,
        hover_name=name_col,
        hover_data={
            "Full_Address": True,
            aum_col: True,
            type_col: True,
            "Score": "Score" in df.columns
        },
        title="Prospect Map (Mapbox Scatter)"
    )
    fig.update_layout(mapbox_style="streets", margin=dict(l=0, r=0, t=30, b=0))
    return fig
