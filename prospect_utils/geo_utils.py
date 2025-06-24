import plotly.express as px
import pandas as pd

def plot_us_map(df):
    """
    Plots a choropleth map of the U.S. by state with average or total scores.
    Falls back to AUM if no scores present.
    """
    if "Score" in df.columns:
        agg = df.groupby("State").agg(
            Avg_Score=("Score", "mean"),
            Total_AUM=("AUM", "sum"),
            Count=("Company", "count")
        ).reset_index()
        color_col = "Avg_Score"
        hover_data = ["Total_AUM", "Count"]
    else:
        agg = df.groupby("State").agg(
            Total_AUM=("AUM", "sum"),
            Count=("Company", "count")
        ).reset_index()
        color_col = "Total_AUM"
        hover_data = ["Count"]

    fig = px.choropleth(
        agg,
        locations="State",
        locationmode="USA-states",
        color=color_col,
        hover_name="State",
        hover_data=hover_data,
        scope="usa",
        color_continuous_scale="Blues",
        title="U.S. Prospect Heatmap"
    )
    fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    return fig
