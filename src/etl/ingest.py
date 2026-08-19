from pathlib import Path

import pandas as pd


RAW_FILE = Path("data/raw/Sample - Superstore.csv")


def load_raw_data() -> pd.DataFrame:
    """Load the raw Superstore CSV into a Pandas DataFrame."""
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_FILE}")

    return pd.read_csv(
        RAW_FILE,
        encoding="latin1",
    )


if __name__ == "__main__":
    df = load_raw_data()

    print("Raw dataset loaded successfully.")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
