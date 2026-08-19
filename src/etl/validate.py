import pandas as pd


REQUIRED_COLUMNS = {
    "row_id",
    "order_id",
    "order_date",
    "ship_date",
    "ship_mode",
    "customer_id",
    "customer_name",
    "segment",
    "country",
    "city",
    "state",
    "postal_code",
    "region",
    "product_id",
    "category",
    "sub_category",
    "product_name",
    "sales",
    "quantity",
    "discount",
    "profit",
}


def validate_data(df: pd.DataFrame) -> None:
    """Validate transformed Superstore data."""

    if df.empty:
        raise ValueError("Dataset is empty.")

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    if df.isnull().any().any():
        raise ValueError("Dataset contains missing values.")

    if df.duplicated().any():
        raise ValueError("Dataset contains duplicate rows.")

    if (df["sales"] < 0).any():
        raise ValueError("Dataset contains negative sales values.")

    if (df["quantity"] <= 0).any():
        raise ValueError("Dataset contains invalid quantity values.")

    if not df["discount"].between(0, 1).all():
        raise ValueError("Dataset contains invalid discount values.")

    if (df["order_date"] > df["ship_date"]).any():
        raise ValueError("Some orders have a ship date before the order date.")

    print("Data validation passed.")
