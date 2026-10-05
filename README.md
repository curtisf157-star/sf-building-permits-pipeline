# sf-building-permits-pipeline
[clean_permits.py](https://github.com/user-attachments/files/33065595/clean_permits.py)
# clean_permits.py
import re
import pandas as pd
import numpy as np
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_PATH   = HERE / "Building_Permits.csv"
CLEAN_PATH = HERE / "Building_Permits_clean.csv"

print("Script folder :", HERE)
print("CSV path      :", RAW_PATH)
print("CSV exists?   :", RAW_PATH.exists())

if not RAW_PATH.exists():
    raise FileNotFoundError(f"Could not find Building_Permits.csv in {HERE}")

# --------------------------------------------------
# 1. Load
# --------------------------------------------------
df = pd.read_csv(
    RAW_PATH,
    dtype={
        "Permit Number": "string",
        "Block": "string",
        "Lot": "string",
        "Street Number": "string",
        "Zipcode": "string",
        "Record ID": "string",
    },
    na_values=["", " ", "NA", "N/A", "n/a", "null", "None", "none", "-"],
    keep_default_na=True,
    low_memory=False,
)

print("Shape:", df.shape)

# --------------------------------------------------
# 2. Normalize column names
# --------------------------------------------------
def clean_col_name(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[^0-9a-z]+", "_", col)
    col = re.sub(r"_+", "_", col).strip("_")
    return col

df.columns = [clean_col_name(c) for c in df.columns]

# --------------------------------------------------
# 3. Strip whitespace / normalize strings
# --------------------------------------------------
str_cols = df.select_dtypes(include=["object", "string"]).columns
for c in str_cols:
    df[c] = df[c].astype("string").str.strip()
    df[c] = df[c].replace({"": pd.NA})

# --------------------------------------------------
# 4. Dates
# --------------------------------------------------
date_cols = [
    "permit_creation_date",
    "current_status_date",
    "filed_date",
    "issued_date",
    "completed_date",
    "first_construction_document_date",
    "permit_expiration_date",
]
for c in date_cols:
    df[c] = pd.to_datetime(df[c], format="%m/%d/%Y", errors="coerce")

# --------------------------------------------------
# 5. Booleans (before numeric so they don't get clobbered)
# --------------------------------------------------
bool_cols = [
    "structural_notification",
    "voluntary_soft_story_retrofit",
    "fire_only_permit",
    "tidf_compliance",
    "site_permit",
]

def to_bool(x):
    if pd.isna(x):
        return pd.NA
    s = str(x).strip().lower()
    if s in {"y", "yes", "true", "t", "1"}:
        return True
    if s in {"n", "no", "false", "f", "0"}:
        return False
    return pd.NA

for c in bool_cols:
    if c in df.columns:
        df[c] = df[c].map(to_bool).astype("boolean")

# --------------------------------------------------
# 6. Location -> lat / lon
# --------------------------------------------------
if "location" in df.columns:
    loc = df["location"].str.extract(r"\(([^,]+),\s*([^)]+)\)")
    df["latitude"]  = pd.to_numeric(loc[0], errors="coerce").astype("Float64")
    df["longitude"] = pd.to_numeric(loc[1], errors="coerce").astype("Float64")

# --------------------------------------------------
# 7. Numeric: integers as Int64, money as Float64
# --------------------------------------------------
int_like_cols = [
    "permit_type",
    "unit",
    "supervisor_district",
    "number_of_existing_stories",
    "number_of_proposed_stories",
    "existing_units",
    "proposed_units",
    "plansets",
    "existing_construction_type",
    "proposed_construction_type",
]

for c in int_like_cols:
    if c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        # Round so 3.0000001 or 2.9999998 don't break Int64 casting
        df[c] = s.round().astype("Int64")

money_cols = ["estimated_cost", "revised_cost"]
for c in money_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Float64")

# --------------------------------------------------
# 8. Zipcode -> 5-digit string
# --------------------------------------------------
if "zipcode" in df.columns:
    df["zipcode"] = (
        df["zipcode"].astype("string")
        .str.extract(r"(\d{5})", expand=False)
        .astype("string")
    )

# --------------------------------------------------
# 9. Drop exact duplicates & rows without a permit number
# --------------------------------------------------
df = df.drop_duplicates()
if "permit_number" in df.columns:
    df = df[df["permit_number"].notna()].copy()
    df["permit_number"] = df["permit_number"].str.strip()

# --------------------------------------------------
# 10. Sanity checks
# --------------------------------------------------
if {"latitude", "longitude"}.issubset(df.columns):
    bad = (
        (df["latitude"] < 37.70) | (df["latitude"] > 37.83) |
        (df["longitude"] < -122.52) | (df["longitude"] > -122.35)
    )
    print(f"Rows with out-of-SF coordinates: {bad.sum()}")
    df.loc[bad, ["latitude", "longitude"]] = pd.NA

if "permit_number" in df.columns:
    print("Duplicate permit_number rows:", df["permit_number"].duplicated().sum())

# Normalize common text categories
for c in ["current_status", "permit_type_definition",
          "existing_use", "proposed_use",
          "neighborhoods_analysis_boundaries"]:
    if c in df.columns:
        df[c] = df[c].astype("string").str.strip().str.title()

# --------------------------------------------------
# 11. Final validation
# --------------------------------------------------
print("\nAfter cleaning:")
print("Shape:", df.shape)
print(df.dtypes)
print("\nMissing values (top 20):")
print(df.isna().sum().sort_values(ascending=False).head(20))

for c in date_cols:
    if c in df.columns and df[c].notna().any():
        print(f"{c}: {df[c].min()} -> {df[c].max()}")
# Derived: how long from filing to completion (where both exist)
if {"filed_date", "completed_date"}.issubset(df.columns):
    df["duration_days"] = (df["completed_date"] - df["filed_date"]).dt.days.astype("Int64")

# Derived: filed year / month for easy grouping
if "filed_date" in df.columns:
    df["filed_year"]  = df["filed_date"].dt.year.astype("Int64")
    df["filed_month"] = df["filed_date"].dt.month.astype("Int64")

# Derived: full address string
addr_cols = ["street_number", "street_name", "street_suffix"]
if all(c in df.columns for c in addr_cols):
    df["full_address"] = (
        df["street_number"].astype("string").fillna("") + " " +
        df["street_name"].astype("string").fillna("") + " " +
        df["street_suffix"].astype("string").fillna("")
    ).str.replace(r"\s+", " ", regex=True).str.strip().astype("string")
# --------------------------------------------------
# 12. Save  <-- MUST be last
# --------------------------------------------------
df.to_csv(CLEAN_PATH, index=False)
print(f"\nSaved cleaned file to: {CLEAN_PATH}")
