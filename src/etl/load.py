import os

import mysql.connector
import pandas as pd
from dotenv import load_dotenv

from src.etl.ingest import load_raw_data
from src.etl.transform import transform_data


load_dotenv()


def get_connection():
    """Create a connection to the cloud_analytics database."""
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
    )


def load_customers(connection, df):
    """Load customers into dim_customer."""

    customers = df[
        ["customer_id", "customer_name", "segment"]
    ].drop_duplicates()

    query = """
        INSERT INTO dim_customer
            (customer_id, customer_name, segment)
        VALUES
            (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            customer_name = VALUES(customer_name),
            segment = VALUES(segment)
    """

    cursor = connection.cursor()

    records = list(
        customers.itertuples(index=False, name=None)
    )

    cursor.executemany(query, records)
    connection.commit()
    cursor.close()

    print(f"Customers loaded: {len(records):,}")


def load_products(connection, df):
    """Load products into dim_product."""

    products = df[
        [
            "product_id",
            "product_name",
            "category",
            "sub_category",
        ]
    ].drop_duplicates()

    query = """
        INSERT INTO dim_product
            (product_id, product_name, category, sub_category)
        VALUES
            (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            category = VALUES(category),
            sub_category = VALUES(sub_category)
    """

    cursor = connection.cursor()

    records = list(
        products.itertuples(index=False, name=None)
    )

    cursor.executemany(query, records)
    connection.commit()
    cursor.close()

    print(f"Products loaded: {len(records):,}")


def load_locations(connection, df):
    """Load locations into dim_location."""

    locations = df[
        [
            "country",
            "state",
            "city",
            "postal_code",
            "region",
        ]
    ].drop_duplicates()

    query = """
        INSERT INTO dim_location
            (country, state, city, postal_code, region)
        VALUES
            (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            region = VALUES(region)
    """

    cursor = connection.cursor()

    records = list(
        locations.itertuples(index=False, name=None)
    )

    cursor.executemany(query, records)
    connection.commit()
    cursor.close()

    print(f"Locations loaded: {len(records):,}")


def load_dates(connection, df):
    """Load calendar dates into dim_date."""

    start_date = min(
        df["order_date"].min(),
        df["ship_date"].min(),
    )

    end_date = max(
        df["order_date"].max(),
        df["ship_date"].max(),
    )

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    records = []

    for date in dates:
        records.append(
            (
                int(date.strftime("%Y%m%d")),
                date.date(),
                date.year,
                (date.month - 1) // 3 + 1,
                date.month,
                date.strftime("%B"),
                int(date.isocalendar().week),
                date.day,
            )
        )

    query = """
        INSERT INTO dim_date
            (
                date_key,
                full_date,
                year,
                quarter,
                month,
                month_name,
                week,
                day
            )
        VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            year = VALUES(year),
            quarter = VALUES(quarter),
            month = VALUES(month),
            month_name = VALUES(month_name),
            week = VALUES(week),
            day = VALUES(day)
    """

    cursor = connection.cursor()

    cursor.executemany(query, records)
    connection.commit()
    cursor.close()

    print(f"Dates loaded: {len(records):,}")


def load_sales(connection, df):
    """Load sales transactions into fact_sales."""

    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT customer_key, customer_id
        FROM dim_customer
        """
    )

    customer_map = {
        row["customer_id"]: row["customer_key"]
        for row in cursor.fetchall()
    }

    cursor.execute(
        """
        SELECT product_key, product_id, product_name
        FROM dim_product
        """
    )

    product_map = {
        (row["product_id"], row["product_name"]): row["product_key"]
        for row in cursor.fetchall()
    }

    cursor.execute(
        """
        SELECT location_key, country, state, city, postal_code
        FROM dim_location
        """
    )

    location_map = {
        (
            row["country"],
            row["state"],
            row["city"],
            row["postal_code"],
        ): row["location_key"]
        for row in cursor.fetchall()
    }

    cursor.close()

    records = []

    for row in df.itertuples(index=False):

        date_key = int(row.order_date.strftime("%Y%m%d"))

        customer_key = customer_map[row.customer_id]

        product_key = product_map[
            (row.product_id, row.product_name)
        ]

        location_key = location_map[
            (
                row.country,
                row.state,
                row.city,
                row.postal_code,
            )
        ]

        records.append(
            (
                row.order_id,
                date_key,
                customer_key,
                product_key,
                location_key,
                row.ship_date.date(),
                row.ship_mode,
                int(row.quantity),
                float(row.sales),
                float(row.discount),
                float(row.profit),
            )
        )

    query = """
        INSERT INTO fact_sales
            (
                order_id,
                date_key,
                customer_key,
                product_key,
                location_key,
                ship_date,
                ship_mode,
                quantity,
                sales,
                discount,
                profit
            )
        VALUES
            (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
    """

    cursor = connection.cursor()

    cursor.executemany(query, records)
    connection.commit()
    cursor.close()

    print(f"Sales loaded: {len(records):,}")


if __name__ == "__main__":

    connection = get_connection()

    try:
        df = load_raw_data()
        df = transform_data(df)

        load_customers(connection, df)
        load_products(connection, df)
        load_locations(connection, df)
        load_dates(connection, df)
        load_sales(connection, df)

    finally:
        connection.close()
