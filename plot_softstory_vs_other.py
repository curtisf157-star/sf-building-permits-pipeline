import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)

df["kind"] = np.where(
    df["description"].astype("string").str.contains(
        "soft story|soft-story", case=False, na=False, regex=True),
    "Soft-story",
    np.where(
        df["permit_type_definition"].eq("Additions Alterations Or Repairs"),
        "Other alterations",
        "Everything else"
    )
)

# Only Completed permits so durations are comparable
done = df[df["current_status"].eq("Complete")].copy()
done = done[done["duration_days"].isna() | (done["duration_days"] >= 0)]
done["duration_days"] = pd.to_numeric(done["duration_days"], errors="coerce")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Duration box plot
ax = axes[0, 0]
groups = [done.loc[done["kind"].eq(k), "duration_days"].dropna()
          for k in ["Soft-story", "Other alterations"]]
ax.boxplot(groups, labels=["Soft-story", "Other alterations"], showfliers=False)
ax.set_title("Duration (filed -> completed) — Completed permits only")
ax.set_ylabel("days")

# 2. Median cost comparison
ax = axes[0, 1]
med = done.groupby("kind")["estimated_cost"].median().reindex(
    ["Soft-story", "Other alterations", "Everything else"])
med.plot(kind="bar", ax=ax, color=["purple", "steelblue", "grey"])
ax.set_title("Median estimated cost")
ax.set_ylabel("USD")
ax.tick_params(axis="x", rotation=15)

# 3. Completion rate by filed year
ax = axes[1, 0]
for k, color in [("Soft-story", "purple"), ("Other alterations", "steelblue")]:
    sub = df[df["kind"].eq(k)]
    t = sub.groupby("filed_year").agg(
        total=("permit_number", "size"),
        comp=("completed_date", lambda s: s.notna().sum()))
    (t["comp"] / t["total"]).plot(ax=ax, label=k, color=color, marker="o")
ax.set_title("Completion rate by filed year")
ax.set_ylabel("share completed")
ax.set_ylim(0, 1)
ax.legend()

# 4. Cost distribution (log)
ax = axes[1, 1]
for k, color in [("Soft-story", "purple"), ("Other alterations", "steelblue")]:
    c = df.loc[df["kind"].eq(k), "estimated_cost"]
    c = c[c > 0]
    ax.hist(c, bins=50, alpha=0.5, label=k, color=color)
ax.set_xscale("log")
ax.set_title("Estimated cost distribution (log)")
ax.set_xlabel("USD (log)")
ax.legend()

plt.tight_layout()
plt.savefig("softstory_vs_other.png", dpi=120)
print("Saved softstory_vs_other.png")

# numbers
print("\nCompleted duration (days) — median, p75, p90:")
for k in ["Soft-story", "Other alterations"]:
    s = done.loc[done["kind"].eq(k), "duration_days"].dropna()
    print(f"  {k:<20} median={s.median():.0f}  p75={s.quantile(.75):.0f}  p90={s.quantile(.90):.0f}")

print("\nMedian estimated cost by kind:")
print(done.groupby("kind")["estimated_cost"].median())

print("\nTotal soft-story estimated spend:")
ss_total = df.loc[df["kind"].eq("Soft-story"), "estimated_cost"].sum()
print(f"  ${ss_total:,.0f}")