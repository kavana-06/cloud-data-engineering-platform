import os
import time
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
CSV_FILE = BASE_DIR / "data" / "raw" / "Superstore.csv"

load_dotenv(BASE_DIR / ".env")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    for attempt in range(1, 11):
        try:
            connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST", "localhost"),
                port=int(os.getenv("MYSQL_PORT", "3306")),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE", "cloud_analytics"),
            )

            print("Database connection successful.")
            return connection

        except mysql.connector.Error as error:
            print(
                f"MySQL connection attempt {attempt}/10 failed: {error}"
            )

            if attempt < 10:
                time.sleep(2)

    raise RuntimeError(
        "Could not connect to MySQL after 10 attempts."
    )


# ============================================================
# LOAD AND CLEAN CSV
# ============================================================

def load_raw_data():
    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_FILE}"
        )

    print(f"Reading CSV: {CSV_FILE}")

    df = pd.read_csv(
        CSV_FILE,
        encoding="latin1"
    )

    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    print(f"Rows loaded: {len(df)}")

    # Convert dates
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    df["ship_date"] = pd.to_datetime(
        df["ship_date"],
        errors="coerce"
    )

    # Convert numeric columns
    df["postal_code"] = pd.to_numeric(
        df["postal_code"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["quantity"] = pd.to_numeric(
        df["quantity"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["sales"] = pd.to_numeric(
        df["sales"],
        errors="coerce"
    ).fillna(0)

    df["discount"] = pd.to_numeric(
        df["discount"],
        errors="coerce"
    ).fillna(0)

    df["profit"] = pd.to_numeric(
        df["profit"],
        errors="coerce"
    ).fillna(0)

    # Remove invalid dates
    df = df.dropna(
        subset=["order_date", "ship_date"]
    ).copy()

    print(f"Clean rows: {len(df)}")

    return df


# ============================================================
# CUSTOMERS
# ============================================================

def load_customers(connection, df):

    cursor = connection.cursor()

    query = """
        INSERT INTO dim_customer
        (
            customer_id,
            customer_name,
            segment
        )
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            customer_name = VALUES(customer_name),
            segment = VALUES(segment)
    """

    data = (
        df[
            [
                "customer_id",
                "customer_name",
                "segment"
            ]
        ]
        .drop_duplicates(
            subset=["customer_id"]
        )
        .itertuples(
            index=False,
            name=None
        )
    )

    cursor.executemany(
        query,
        list(data)
    )

    connection.commit()
    cursor.close()

    print(
        f"Customers loaded: {df['customer_id'].nunique()}"
    )


# ============================================================
# PRODUCTS
# ============================================================

def load_products(connection, df):

    cursor = connection.cursor()

    query = """
        INSERT INTO dim_product
        (
            product_id,
            product_name,
            category,
            sub_category
        )
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            category = VALUES(category),
            sub_category = VALUES(sub_category)
    """

    data = (
        df[
            [
                "product_id",
                "product_name",
                "category",
                "sub_category"
            ]
        ]
        .drop_duplicates(
            subset=[
                "product_id",
                "product_name"
            ]
        )
        .itertuples(
            index=False,
            name=None
        )
    )

    records = list(data)

    cursor.executemany(
        query,
        records
    )

    connection.commit()
    cursor.close()

    print(
        f"Products loaded: {len(records)}"
    )


# ============================================================
# LOCATIONS
# ============================================================

def load_locations(connection, df):

    cursor = connection.cursor()

    query = """
        INSERT INTO dim_location
        (
            country,
            state,
            city,
            postal_code,
            region
        )
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            region = VALUES(region)
    """

    data = (
        df[
            [
                "country",
                "state",
                "city",
                "postal_code",
                "region"
            ]
        ]
        .drop_duplicates(
            subset=[
                "country",
                "state",
                "city",
                "postal_code"
            ]
        )
        .itertuples(
            index=False,
            name=None
        )
    )

    records = list(data)

    cursor.executemany(
        query,
        records
    )

    connection.commit()
    cursor.close()

    print(
        f"Locations loaded: {len(records)}"
    )


# ============================================================
# DATES
# ============================================================

def load_dates(connection, df):

    cursor = connection.cursor()

    dates = (
        df[["order_date"]]
        .drop_duplicates()
        .copy()
    )

    dates["date_key"] = (
        dates["order_date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    dates["year"] = (
        dates["order_date"]
        .dt.year
        .astype(int)
    )

    dates["quarter"] = (
        "Q"
        + dates["order_date"]
        .dt.quarter
        .astype(str)
    )

    dates["month"] = (
        dates["order_date"]
        .dt.month
        .astype(int)
    )

    dates["month_name"] = (
        dates["order_date"]
        .dt.strftime("%B")
    )

    dates["week"] = (
        dates["order_date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    dates["day"] = (
        dates["order_date"]
        .dt.day
        .astype(int)
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
        (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            year = VALUES(year),
            quarter = VALUES(quarter),
            month = VALUES(month),
            month_name = VALUES(month_name),
            week = VALUES(week),
            day = VALUES(day)
    """

    records = (
        dates[
            [
                "date_key",
                "order_date",
                "year",
                "quarter",
                "month",
                "month_name",
                "week",
                "day"
            ]
        ]
        .itertuples(
            index=False,
            name=None
        )
    )

    records = list(records)

    cursor.executemany(
        query,
        records
    )

    connection.commit()
    cursor.close()

    print(
        f"Dates loaded: {len(records)}"
    )


# ============================================================
# DIMENSION LOOKUPS
# ============================================================

def get_customer_keys(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT customer_id, customer_key
        FROM dim_customer
        """
    )

    result = dict(cursor.fetchall())

    cursor.close()

    return result


def get_product_keys(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            product_id,
            product_name,
            product_key
        FROM dim_product
        """
    )

    result = {
        (row[0], row[1]): row[2]
        for row in cursor.fetchall()
    }

    cursor.close()

    return result


def get_location_keys(connection):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            country,
            state,
            city,
            postal_code,
            location_key
        FROM dim_location
        """
    )

    result = {
        (
            row[0],
            row[1],
            row[2],
            row[3]
        ): row[4]
        for row in cursor.fetchall()
    }

    cursor.close()

    return result


# ============================================================
# FACT SALES
# ============================================================

def load_fact_sales(connection, df):

    cursor = connection.cursor()

    customer_keys = get_customer_keys(connection)
    product_keys = get_product_keys(connection)
    location_keys = get_location_keys(connection)

    # Clear previous fact data so the ETL can be
    # safely executed multiple times.
    cursor.execute(
        "DELETE FROM fact_sales"
    )

    connection.commit()

    records = []

    for row in df.itertuples(index=False):

        customer_key = customer_keys.get(
            row.customer_id
        )

        product_key = product_keys.get(
            (
                row.product_id,
                row.product_name
            )
        )

        location_key = location_keys.get(
            (
                row.country,
                row.state,
                row.city,
                int(row.postal_code)
            )
        )

        if customer_key is None:
            continue

        if product_key is None:
            continue

        if location_key is None:
            continue

        date_key = int(
            row.order_date.strftime("%Y%m%d")
        )

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
                float(row.profit)
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

    cursor.executemany(
        query,
        records
    )

    connection.commit()
    cursor.close()

    print(
        f"Sales rows loaded: {len(records)}"
    )


# ============================================================
# MAIN ETL PIPELINE
# ============================================================

def main():

    print("Starting ETL pipeline...")

    df = load_raw_data()

    connection = get_connection()

    try:

        load_customers(
            connection,
            df
        )

        load_products(
            connection,
            df
        )

        load_locations(
            connection,
            df
        )

        load_dates(
            connection,
            df
        )

        load_fact_sales(
            connection,
            df
        )

        print()
        print("=" * 60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    finally:

        connection.close()

        print(
            "MySQL connection closed."
        )


if __name__ == "__main__":
    main()
