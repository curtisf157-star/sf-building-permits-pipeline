import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)

# ---- filter to real, completed work ----
done = df[df["current_status"].eq("Complete")].copy()
done = done[done["duration_days"].isna() | (done["duration_days"] >= 0)]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Permit type mix (top 6)
ax = axes[0, 0]
df["permit_type_definition"].value_counts().head(6).plot(
    kind="barh", ax=ax, color="steelblue"
)
ax.set_title("Permits by type")
ax.invert_yaxis()

# 2. Status breakdown
ax = axes[0, 1]
df["current_status"].value_counts().head(6).plot(
    kind="barh", ax=ax, color="coral"
)
ax.set_title("Current status")
ax.invert_yaxis()

# 3. Median estimated cost by permit type (log scale)
ax = axes[1, 0]
med = (
    df.groupby("permit_type_definition")["estimated_cost"]
      .median()
      .dropna()
      .sort_values()
)
ax.barh(med.index, med.values, color="seagreen")
ax.set_xscale("log")
ax.set_title("Median estimated cost by permit type (log)")
ax.set_xlabel("USD (log scale)")

# 4. Completion rate by filed year
ax = axes[1, 1]
tmp = df.groupby("filed_year").agg(
    total=("permit_number", "size"),
    completed=("completed_date", lambda s: s.notna().sum()),
)
tmp["rate"] = tmp["completed"] / tmp["total"]
tmp["rate"].plot(kind="bar", ax=ax, color="purple")
ax.set_title("Completion rate by filed year\n(data cut off Feb 2018)")
ax.set_ylabel("share completed")
ax.set_ylim(0, 1)

plt.tight_layout()
plt.savefig("permits_overview.png", dpi=120)
print("Saved permits_overview.png")