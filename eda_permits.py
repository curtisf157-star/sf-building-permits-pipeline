import pandas as pd
import numpy as np

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)

# 1. Permit type mix
print("\n=== Permit type definitions (top 10) ===")
print(df["permit_type_definition"].value_counts().head(10))

# 2. Status breakdown
print("\n=== Current status ===")
print(df["current_status"].value_counts())

# 3. Permits per year
print("\n=== Permits per filed year ===")
print(df["filed_year"].value_counts().sort_index())

# 4. Top neighbourhoods by permit count
print("\n=== Top 10 neighbourhoods by permit count ===")
print(df["neighborhoods_analysis_boundaries"].value_counts().head(10))

# 5. Cost stats
print("\n=== Estimated cost describe (raw) ===")
print(df["estimated_cost"].describe())

# 6. Cost by permit type
print("\n=== Median estimated cost by permit type ===")
print(
    df.groupby("permit_type_definition")["estimated_cost"]
      .median()
      .sort_values(ascending=False)
      .head(10)
)

# 7. How long do permits take?
print("\n=== Duration (filed -> completed), in days ===")
print(df["duration_days"].describe())

# 8. Completion rate by year
print("\n=== Completion rate by filed year ===")
tmp = df.groupby("filed_year").agg(
    total=("permit_number", "size"),
    completed=("completed_date", lambda s: s.notna().sum()),
)
tmp["completion_rate"] = (tmp["completed"] / tmp["total"]).round(3)
print(tmp)
