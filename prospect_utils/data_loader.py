import pandas as pd
import difflib


def clean_address_field(val):
    if pd.isna(val):
        return ""
    val = str(val).encode("ascii", "ignore").decode("utf-8")
    val = val.replace("\n", " ").replace("\r", " ")
    val = val.replace("’", "'").replace("“", '"').replace("”", '"')
    return val.strip()


def prepare_address_dataframe(df):
    """
    Cleans and prepares address columns, returning a DataFrame with a 'Full_Address' column.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\xa0", " ")
        .str.replace(" +", " ", regex=True)
    )

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
            # Return empty DataFrame if required column is missing
            return pd.DataFrame()

    street_col = required_fields["Dakota Billing Street"]
    city_col = required_fields["Dakota Billing City"]
    state_col = required_fields["Dakota Billing State/Province"]
    zip_col = required_fields["Dakota Billing Zip/Postal Code"]

    country_col = next((c for c in df.columns if "Country" in c), None)
    if country_col:
        df = df[df[country_col].fillna("").str.upper() == "UNITED STATES"].copy()

    df = df.dropna(subset=[street_col, city_col, state_col, zip_col])
    for col in [street_col, city_col, state_col, zip_col]:
        df[col] = df[col].apply(clean_address_field)

    df = df[
        df[[street_col, city_col, state_col, zip_col]].apply(lambda row: all(str(x).strip() for x in row), axis=1)
    ].copy()

    try:
        df["Full_Address"] = (
            df[street_col] + ", " +
            df[city_col] + ", " +
            df[state_col] + " " +
            df[zip_col].astype(str)
        )
    except Exception:
        return pd.DataFrame()

    df = df[df["Full_Address"].str.len() > 10]
    return df 