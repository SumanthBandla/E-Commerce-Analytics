"""
data_cleaning.py
================
Data cleaning and preprocessing for the E-Commerce Analytics project.

Workflow
--------
1.  Load the raw dataset
2.  Inspect shape, data types, missing values and duplicates
3.  Handle missing values
4.  Convert "Order Date" to datetime
5.  Validate numerical columns (sales, profit, quantity, discount)
6.  Detect invalid sales / profit values
7.  Check inconsistent categorical values
8.  Create derived columns (Year, Month, Quarter, Profit Margin, Year-Month)
9.  Save the cleaned dataset and a cleaning report

Input  : data/ecommerce_dataset.csv
Output : outputs/cleaned_data/ecommerce_clean.csv
         outputs/cleaned_data/data_cleaning_report.txt
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths (resolved relative to the project root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "ecommerce_dataset.csv"
CLEAN_PATH = PROJECT_ROOT / "outputs" / "cleaned_data" / "ecommerce_clean.csv"
REPORT_PATH = PROJECT_ROOT / "outputs" / "cleaned_data" / "data_cleaning_report.txt"

# Columns whose cardinality / values we want to inspect for consistency
CATEGORICAL_COLUMNS = [
    "Segment", "Country", "State", "Region", "Category", "Sub-Category",
    "Shipping Mode", "Payment Mode",
]

NUMERIC_COLUMNS = ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _log(lines: list[str], message: str = "") -> None:
    """Append a message to the report lines list and optionally print it."""
    lines.append(message)


def _separator() -> str:
    return "=" * 70


# ---------------------------------------------------------------------------
# Cleaning pipeline
# ---------------------------------------------------------------------------
def load_data(path: Path, lines: list[str]) -> pd.DataFrame:
    _log(lines, _separator())
    _log(lines, "STEP 1: LOAD RAW DATASET")
    _log(lines, _separator())
    df = pd.read_csv(path, encoding="utf-8-sig")
    _log(lines, f"Raw dataset loaded from: {path.name}")
    _log(lines, f"Dataset shape (rows, columns): {df.shape}")
    _log(lines, "")
    _log(lines, "Column names:")
    for col in df.columns:
        _log(lines, f"    - {col}")
    _log(lines, "")
    _log(lines, "First 5 rows (preview):")
    for row in df.head(5).to_string().splitlines():
        _log(lines, f"    {row}")
    return df


def inspect_dtypes(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 2: CHECK DATA TYPES")
    _log(lines, _separator())
    dtype_summary = df.dtypes.astype(str).to_frame(name="dtype")
    _log(lines, dtype_summary.to_string())
    _log(lines, "")
    _log(lines, f"Object (text) columns: {df.select_dtypes('str').shape[1]}")
    _log(lines, f"Numerical columns: {df.select_dtypes('number').shape[1]}")
    return df


def check_missing_values(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 3: CHECK MISSING VALUES")
    _log(lines, _separator())
    missing = df.isna().sum()
    missing = missing[missing > 0]
    if missing.empty:
        _log(lines, "No missing values found.")
    else:
        _log(lines, "Columns with missing values (count / percentage):")
        for col, count in missing.items():
            pct = 100.0 * count / len(df)
            _log(lines, f"    {col}: {count}  ({pct:.2f}%)")
    return df


def handle_missing_values(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 4: HANDLE MISSING VALUES")
    _log(lines, _separator())
    missing = df.isna().sum()
    missing = missing[missing > 0]

    if missing.empty:
        _log(lines, "No action required (no missing values).")
        return df

    for col in missing.index:
        if col == "Shipping Cost":
            # Numeric column -> impute with the median (robust to outliers).
            median = df[col].median()
            n_before = int(df[col].isna().sum())
            df[col] = df[col].fillna(median)
            _log(lines, f"    {col}: imputed {n_before} missing values with median ({median:.2f}).")
        elif col in CATEGORICAL_COLUMNS:
            # Categorical column -> fill with the mode (most common value).
            mode_val = df[col].mode().iloc[0]
            n_before = int(df[col].isna().sum())
            df[col] = df[col].fillna(mode_val)
            _log(lines, f"    {col}: filled {n_before} missing values with mode ('{mode_val}').")
        else:
            # Any other column -> drop rows where it is missing.
            n_before = int(df[col].isna().sum())
            df = df.dropna(subset=[col]).reset_index(drop=True)
            _log(lines, f"    {col}: dropped {n_before} rows with missing values.")

    _log(lines, f"Remaining missing values after cleaning: {int(df.isna().sum().sum())}")
    return df


def check_duplicates(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 5: CHECK DUPLICATE ORDERS")
    _log(lines, _separator())
    n_duplicates = int(df.duplicated().sum())
    if n_duplicates == 0:
        _log(lines, "No fully-duplicated rows found.")
        return df
    _log(lines, f"Fully-duplicated rows found: {n_duplicates}")
    _log(lines, f"Removing {n_duplicates} duplicated row(s)...")
    df = df.drop_duplicates().reset_index(drop=True)
    _log(lines, f"Rows after de-duplication: {len(df)}")
    return df


def convert_dates(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 6: CONVERT 'Order Date' TO DATETIME")
    _log(lines, _separator())
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    n_bad = int(df["Order Date"].isna().sum())
    if n_bad > 0:
        _log(lines, f"Warning: {n_bad} invalid date(s) found. Dropping them.")
        df = df.dropna(subset=["Order Date"]).reset_index(drop=True)
    _log(lines, f"Date range: {df['Order Date'].min().date()} to {df['Order Date'].max().date()}")
    return df


def validate_numerical_columns(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 7: VALIDATE NUMERICAL COLUMNS")
    _log(lines, _separator())
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    n_bad = int(df[NUMERIC_COLUMNS].isna().sum().sum())
    if n_bad > 0:
        _log(lines, f"Warning: {n_bad} non-numeric / missing value(s) in numerical columns. Dropping them.")
        df = df.dropna(subset=NUMERIC_COLUMNS).reset_index(drop=True)

    _log(lines, "Descriptive statistics for numerical columns:")
    stats = df[NUMERIC_COLUMNS].describe().T
    for idx, row in stats.iterrows():
        _log(lines, (
            f"    {idx:<14} mean={row['mean']:>12.2f}  min={row['min']:>10.2f}  "
            f"max={row['max']:>12.2f}"
        ))
    return df


def detect_invalid_values(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 8: DETECT INVALID SALES / PROFIT VALUES")
    _log(lines, _separator())

    n_negative_sales = int((df["Sales"] <= 0).sum())
    n_negative_quantity = int((df["Quantity"] <= 0).sum())
    n_discount_out = int(((df["Discount"] < 0) | (df["Discount"] > 1)).sum())
    n_negative_profit = int((df["Profit"] < 0).sum())
    n_zero_shipping = int((df["Shipping Cost"] < 0).sum())

    _log(lines, f"    Rows with Sales <= 0            : {n_negative_sales}")
    _log(lines, f"    Rows with Quantity <= 0         : {n_negative_quantity}")
    _log(lines, f"    Rows with Discount outside [0,1]: {n_discount_out}")
    _log(lines, f"    Rows with negative Profit (losses): {n_negative_profit}  (kept intentionally - losses are valid business data)")
    _log(lines, f"    Rows with negative Shipping Cost : {n_zero_shipping}")

    invalid_mask = (
        (df["Sales"] <= 0)
        | (df["Quantity"] <= 0)
        | (df["Discount"] < 0)
        | (df["Discount"] > 1)
        | (df["Shipping Cost"] < 0)
    )
    n_invalid = int(invalid_mask.sum())
    if n_invalid > 0:
        _log(lines, f"    Removing {n_invalid} row(s) with logically invalid values...")
        df = df[~invalid_mask].reset_index(drop=True)

    _log(lines, "    Note: negative Profit values are legitimate (loss-making orders) and are kept.")
    return df


def check_categorical_consistency(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 9: CHECK INCONSISTENT CATEGORICAL VALUES")
    _log(lines, _separator())

    # Canonical casing per column: raw value -> standard value.
    # Standardising casing (not just title-case) keeps acronyms like "UPI"
    # intact and normalises near-duplicate entries.
    canonical_maps: dict[str, dict[str, str]] = {
        "Segment": {
            "consumer": "Consumer",
            "CONSUMER": "Consumer",
            "corporate": "Corporate",
            "CORPORATE": "Corporate",
            "corporat": "Corporate",
            "home office": "Home Office",
            "HOME OFFICE": "Home Office",
            "homeoffice": "Home Office",
        },
        "Payment Mode": {
            "UPI": "UPI",
            "upi": "UPI",
            "Upi": "UPI",
            "cash on delivery": "Cash on Delivery",
            "CASH ON DELIVERY": "Cash on Delivery",
            "Cash On Delivery": "Cash on Delivery",
            "credit card": "Credit Card",
            "debit card": "Debit Card",
            "net banking": "Net Banking",
        },
        "Shipping Mode": {
            "standard class": "Standard Class",
            "second class": "Second Class",
            "first class": "First Class",
            "same day": "Same Day",
        },
        "Region": {
            "west": "West", "east": "East", "central": "Central", "south": "South",
        },
    }

    n_corrected = 0
    for col in CATEGORICAL_COLUMNS:
        if col not in df.columns:
            continue
        canon = canonical_maps.get(col, {})
        values = df[col].astype(str).str.strip()
        corrected = values.map(lambda v: canon.get(v, v))
        n_corrected += int((corrected != values).sum())
        df[col] = corrected
        _log(lines, f"    {col}: unique values -> {sorted(df[col].unique())}")

    if n_corrected > 0:
        _log(lines, f"    Standardised {n_corrected} inconsistent categorical value(s).")
    else:
        _log(lines, "    No inconsistent categorical values detected.")

    _log(lines, "")
    _log(lines, "Category <-> Sub-Category cross-check (should be internally consistent):")
    cross = (
        df.groupby(["Category", "Sub-Category"])
        .size()
        .reset_index(name="count")
        .to_string(index=False)
    )
    _log(lines, cross)
    return df


def create_derived_columns(df: pd.DataFrame, lines: list[str]) -> pd.DataFrame:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 10: CREATE DERIVED COLUMNS")
    _log(lines, _separator())

    df["Year"] = df["Order Date"].dt.year
    df["Month"] = df["Order Date"].dt.month
    df["Quarter"] = df["Order Date"].dt.quarter
    df["Order Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    # Profit Margin (%) — guarded against division by zero
    df["Profit Margin (%)"] = (df["Profit"] / df["Sales"].replace(0, pd.NA)) * 100
    df["Profit Margin (%)"] = df["Profit Margin (%)"].round(2)

    for col in ["Year", "Month", "Quarter", "Order Year-Month", "Profit Margin (%)"]:
        _log(lines, f"    Created: {col}")

    _log(lines, "")
    _log(lines, "Sample of derived columns:")
    _log(lines, df[["Order Date", "Year", "Month", "Quarter", "Order Year-Month",
                    "Profit Margin (%)"]].head(5).to_string(index=False))
    return df


def save_outputs(df: pd.DataFrame, lines: list[str]) -> None:
    _log(lines, "")
    _log(lines, _separator())
    _log(lines, "STEP 11: SAVE CLEANED DATASET")
    _log(lines, _separator())
    CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    _log(lines, f"Cleaned dataset saved to: {CLEAN_PATH.name}")
    _log(lines, f"Cleaned dataset shape: {df.shape}")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    _log(lines, f"Cleaning report saved to: {REPORT_PATH.name}")
    _log(lines, "")
    _log(lines, "DATA CLEANING COMPLETE.")


def main() -> None:
    report_lines: list[str] = []
    report_lines.append(f"E-COMMERCE ANALYTICS - DATA CLEANING REPORT")
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")

    df = load_data(RAW_PATH, report_lines)
    df = inspect_dtypes(df, report_lines)
    df = check_missing_values(df, report_lines)
    df = handle_missing_values(df, report_lines)
    df = check_duplicates(df, report_lines)
    df = convert_dates(df, report_lines)
    df = validate_numerical_columns(df, report_lines)
    df = detect_invalid_values(df, report_lines)
    df = check_categorical_consistency(df, report_lines)
    df = create_derived_columns(df, report_lines)
    save_outputs(df, report_lines)

    # Print a concise summary to the console
    print(f"Cleaned dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"Saved: {CLEAN_PATH.name} | {REPORT_PATH.name}")


if __name__ == "__main__":
    main()
