import pandas as pd
import pytest

from src.etl.validate import validate_data


def valid_dataframe():
    return pd.DataFrame(
        [
            {
                "row_id": 1,
                "order_id": "CA-001",
                "order_date": pd.Timestamp("2026-01-01"),
                "ship_date": pd.Timestamp("2026-01-03"),
                "ship_mode": "Second Class",
                "customer_id": "C001",
                "customer_name": "Test Customer",
                "segment": "Consumer",
                "country": "United States",
                "city": "New York",
                "state": "New York",
                "postal_code": 10001,
                "region": "East",
                "product_id": "P001",
                "category": "Technology",
                "sub_category": "Phones",
                "product_name": "Test Phone",
                "sales": 100.0,
                "quantity": 2,
                "discount": 0.10,
                "profit": 20.0,
            }
        ]
    )


def test_valid_data_passes():
    df = valid_dataframe()
    validate_data(df)


def test_empty_dataset_fails():
    df = valid_dataframe().iloc[0:0]

    with pytest.raises(ValueError, match="Dataset is empty"):
        validate_data(df)


def test_negative_sales_fails():
    df = valid_dataframe()
    df.loc[0, "sales"] = -10

    with pytest.raises(ValueError, match="negative sales"):
        validate_data(df)


def test_invalid_quantity_fails():
    df = valid_dataframe()
    df.loc[0, "quantity"] = 0

    with pytest.raises(ValueError, match="invalid quantity"):
        validate_data(df)


def test_invalid_discount_fails():
    df = valid_dataframe()
    df.loc[0, "discount"] = 1.5

    with pytest.raises(ValueError, match="invalid discount"):
        validate_data(df)


def test_invalid_shipping_date_fails():
    df = valid_dataframe()
    df.loc[0, "ship_date"] = pd.Timestamp("2025-12-31")

    with pytest.raises(ValueError, match="ship date"):
        validate_data(df)
