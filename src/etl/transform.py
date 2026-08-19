import pandas as pd


def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the raw Superstore dataset."""

    df = df.copy()

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Convert date columns to datetime
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        format="%m/%d/%Y",
    )

    df["ship_date"] = pd.to_datetime(
        df["ship_date"],
        format="%m/%d/%Y",
    )

    return df
