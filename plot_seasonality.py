import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("Building_Permits_clean.csv", low_memory=False)
df["filed_date"] = pd.to_datetime(df["filed_date"], errors="coerce")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Monthly filings, all permits
ax = axes[0, 0]
monthly = df.set_index("filed_date").resample("ME").size()
monthly.plot(ax=ax, color="steelblue")
ax.set_title("Monthly permit filings (all types)")
ax.set_ylabel("permits")

# 2. Monthly filings, soft-story only
ax = axes[0, 1]
ss = df[df["description"].astype("string").str.contains(
    "soft story|soft-story", case=False, na=False, regex=True)]
ss.set_index("filed_date").resample("ME").size().plot(ax=ax, color="purple")
ax.set_title("Monthly filings — soft-story only")
ax.set_ylabel("permits")

# 3. Day of week
ax = axes[1, 0]
dow = (df["filed_date"].dt.day_name()
       .value_counts()
       .reindex(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
       .fillna(0))
dow.plot(kind="bar", ax=ax, color="seagreen")
ax.set_title("Filings by day of week")
ax.set_ylabel("permits")

# 4. Year x Month heatmap
ax = axes[1, 1]
hm = df.groupby([df["filed_date"].dt.year, df["filed_date"].dt.month]).size().unstack()
im = ax.imshow(hm, aspect="auto", cmap="viridis")
ax.set_xticks(range(12))
ax.set_xticklabels(range(1, 13))
ax.set_yticks(range(len(hm)))
ax.set_yticklabels(hm.index)
ax.set_title("Filings — year x month")
ax.set_xlabel("month")
ax.set_ylabel("year")
plt.colorbar(im, ax=ax, label="permits")

plt.tight_layout()
plt.savefig("seasonality_overview.png", dpi=120)
print("Saved seasonality_overview.png")

# numbers
print("\nTop 5 months by filings:")
print(monthly.sort_values(ascending=False).head())
print("\nFilings by weekday:")
print(dow)