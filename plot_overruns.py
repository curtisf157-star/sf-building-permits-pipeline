import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)

# Both costs must be present and estimated must be > 0 to be meaningful
d = df[(df["estimated_cost"] > 0) & (df["revised_cost"] > 0)].copy()

d["overrun_abs"] = d["revised_cost"] - d["estimated_cost"]
d["overrun_pct"] = d["overrun_abs"] / d["estimated_cost"]

print(f"Permits with both cost fields: {len(d):,}")
print(f"Permits that went over:        {(d['overrun_pct'] > 0).sum():,} "
      f"({(d['overrun_pct'] > 0).mean():.1%})")
print(f"Permits exactly on budget:     {(d['overrun_pct'] == 0).sum():,}")
print(f"Permits under budget:          {(d['overrun_pct'] < 0).sum():,}")
print("\nOverrun % describe:")
print(d["overrun_pct"].describe())

# Cap for visual clarity (top 1% are extreme)
cap = d["overrun_pct"].quantile(0.99)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Distribution of overrun %
ax = axes[0, 0]
d["overrun_pct"].clip(-0.5, cap).hist(bins=60, ax=ax, color="firebrick")
ax.axvline(0, color="black", linestyle="--", linewidth=1)
ax.set_title("Distribution of cost overrun %")
ax.set_xlabel("overrun % (clipped at 99th pct)")
ax.set_ylabel("permits")

# 2. Share over budget by permit type
ax = axes[0, 1]
by_type = d.groupby("permit_type_definition").agg(
    n=("overrun_pct", "size"),
    over_rate=("overrun_pct", lambda s: (s > 0).mean())
).query("n >= 100").sort_values("over_rate")
by_type["over_rate"].plot(kind="barh", ax=ax, color="darkorange")
ax.set_title("Share over budget by permit type (n >= 100)")
ax.set_xlabel("share over budget")
ax.invert_yaxis()

# 3. Estimated vs revised (log-log scatter)
ax = axes[1, 0]
sample = d.sample(min(len(d), 20000), random_state=1)
ax.scatter(sample["estimated_cost"], sample["revised_cost"],
           s=3, alpha=0.15, color="teal")
lim = [10, max(d["estimated_cost"].max(), d["revised_cost"].max())]
ax.plot(lim, lim, color="red", linewidth=1, label="y = x (no change)")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(*lim); ax.set_ylim(*lim)
ax.set_xlabel("estimated cost (log)")
ax.set_ylabel("revised cost (log)")
ax.set_title("Estimated vs revised cost")
ax.legend()

# 4. Median overrun % by neighbourhood (top 15)
ax = axes[1, 1]
hood = (d.groupby("neighborhoods_analysis_boundaries")
          .agg(n=("overrun_pct", "size"),
               med=("overrun_pct", "median"))
          .query("n >= 200")
          .sort_values("med", ascending=False)
          .head(15))
hood["med"].plot(kind="barh", ax=ax, color="navy")
ax.set_title("Median overrun % by neighbourhood (n >= 200)")
ax.set_xlabel("median overrun %")
ax.invert_yaxis()

plt.tight_layout()
plt.savefig("overruns_overview.png", dpi=120)
print("Saved overruns_overview.png")