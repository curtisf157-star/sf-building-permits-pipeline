import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)

mask = df["description"].astype("string").str.contains(
    "soft story|soft-story|soft storey|soft-storey",
    case=False, na=False, regex=True
)
ss = df[mask].copy()

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 1. filings per year
ax = axes[0, 0]
ss["filed_year"].value_counts().sort_index().plot(kind="bar", ax=ax, color="teal")
ax.set_title("Soft-story permits filed per year")
ax.set_ylabel("permits")

# 2. completion rate by filed year
ax = axes[0, 1]
tmp = ss.groupby("filed_year").agg(
    total=("permit_number", "size"),
    completed=("completed_date", lambda s: s.notna().sum()),
)
tmp["rate"] = tmp["completed"] / tmp["total"]
tmp["rate"].plot(kind="bar", ax=ax, color="darkgreen")
ax.set_title("Soft-story completion rate by filed year")
ax.set_ylabel("share completed")
ax.set_ylim(0, 1)

# 3. status breakdown
ax = axes[0, 2]
ss["current_status"].value_counts().head(6).plot(kind="barh", ax=ax, color="orange")
ax.set_title("Soft-story — current status")
ax.invert_yaxis()

# 4. top neighbourhoods
ax = axes[1, 0]
ss["neighborhoods_analysis_boundaries"].value_counts().head(10).plot(
    kind="barh", ax=ax, color="indianred")
ax.set_title("Top 10 neighbourhoods — soft-story permits")
ax.invert_yaxis()

# 5. cost distribution (log)
ax = axes[1, 1]
cost = ss["estimated_cost"].dropna()
cost_log = cost[cost > 0]
ax.hist(cost_log, bins=50, color="slateblue")
ax.set_xscale("log")
ax.set_title(f"Soft-story estimated cost (median ${cost.median():,.0f})")
ax.set_xlabel("USD (log scale)")

# 6. map
ax = axes[1, 2]
plot = ss.dropna(subset=["latitude", "longitude"])
ax.scatter(plot["longitude"], plot["latitude"], s=6, alpha=0.4, color="purple")
ax.set_title(f"Soft-story permits on SF map (n={len(plot):,})")
ax.set_xlabel("longitude"); ax.set_ylabel("latitude"); ax.set_aspect("equal")

plt.tight_layout()
plt.savefig("softstory_overview.png", dpi=120)
print("Saved softstory_overview.png")