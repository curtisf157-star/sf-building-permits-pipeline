# San Francisco Building Permits — End-to-End Analysis

An end-to-end data analysis project on **198,900 San Francisco building
permits** filed between January 2013 and February 2018. The goal was to
clean a large, messy public dataset, extract defensible insights, and
build a small portfolio of charts that tell a real story about the city’s
construction pipeline and its mandatory soft-story retrofit programme.

---

## Data

- **Source:** [San Francisco Open Data — Building Permits](https://data.sfgov.org/Housing-and-Buildings/Building-Permits/i98e-djp9)
- **Rows:** 198,900
- **Columns:** 43 raw → 45 cleaned
- **File used:** `Building_Permits.csv` (~79 MB)
- **Output:** `Building_Permits_clean.csv`

---

## Tech stack

| Tool | Purpose |
|---|---|
| **Python 3.13** | Core analysis |
| **pandas** | Loading, cleaning, feature engineering |
| **NumPy** | Numeric operations |
| **Matplotlib** | Static charts |
| **Power BI** | Interactive dashboard |
| **VS Code** | Development environment |

---

## Methodology

### 1. Cleaning (`clean_permits.py`)

- Normalised all column names to `snake_case`.
- Stripped whitespace, converted empty strings to `NA`.
- Cast date columns to `datetime64` with `format="%m/%d/%Y"` and `errors="coerce"`.
- Cast Yes/No flags (`structural_notification`, `fire_only_permit`,
  `site_permit`, etc.) to pandas nullable `boolean`.
- Cast count-like columns (stories, units, plansets, construction types,
  supervisor district) to nullable `Int64`.
- Extracted `latitude` / `longitude` from the raw `Location` string.
- Normalised `zipcode` to 5-digit strings.
- Dropped exact duplicate rows and rows missing a permit number.
- Sanity-checked coordinates against SF bounds (37.70–37.83, -122.52 to -122.35).

**Result:** 198,900 rows, 45 columns, zero errors on reload.

### 2. Feature engineering

- `duration_days` — days from `filed_date` to `completed_date`.
- `filed_year`, `filed_month`.
- `full_address`.

### 3. Analysis modules

| Script | Output | Purpose |
|---|---|---|
| `clean_permits.py` | `Building_Permits_clean.csv` | Data cleaning |
| `plot_permits.py` | `permits_overview.png` | Broad EDA |
| `plot_softstory.py` | `softstory_overview.png` | Soft-story retrofit deep dive |
| `plot_softstory_vs_other.py` | `softstory_vs_other.png` | Comparative analysis |
| `plot_overruns.py` | `overruns_overview.png` | Cost overrun analysis |
| `plot_seasonality.py` | `seasonality_overview.png` | Time-series patterns |
| Power BI dashboard | (link) | Interactive exploration |

---

## Key findings

### 1. Permit mix is dominated by small alterations
**90% of all permits** are over-the-counter (OTC) alterations. Any
city-wide averages are therefore dominated by small jobs — analysis must
be split by permit type.

### 2. Half the permits are still open
Only **49% are Complete**. The rest are Issued (42%), Filed (6%), or in a
terminal non-build state (Withdrawn, Cancelled, Expired). Any analysis of
"work done" must filter on `current_status == "Complete"`.

### 3. Soft-story retrofit filings grew 50× in 5 years