# E-Commerce Analytics — End-to-End Data Analysis

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-3.x-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-2.x-013243?logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-11557C?logo=matplotlib&logoColor=white)
![Seaborn](https://img.shields.io/badge/Seaborn-0.13-4C6EF5)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![Tableau](https://img.shields.io/badge/Tableau-Dashboard-E97627?logo=tableau&logoColor=white)

A complete, portfolio-ready **E-Commerce Data Analysis** project that takes a raw sales
dataset through the full analytics workflow:

> **Raw Dataset → Data Cleaning → EDA → SQL Analysis → Tableau Dashboard → Business Insights**

Built exclusively with descriptive analytics tools — **no machine learning**. Every
result is computed independently in **Python**, **SQL** and **Tableau** and
cross-validated so all KPIs match across every tool.

| | |
|---|---|
| **Repository** | [github.com/SumanthBandla/E-Commerce-Analytics](https://github.com/SumanthBandla/E-Commerce-Analytics) |
| **Dataset** | Synthetic — 5,508 transactions (2019–2023) |
| **Deliverables** | Cleaning pipeline · EDA notebook · 33 SQL queries · Tableau dashboard · Insights |

---

## Table of Contents

1. [Overview](#1-overview)
2. [Business Problem](#2-business-problem)
3. [Objectives](#3-objectives)
4. [Dataset](#4-dataset)
5. [Tech Stack](#5-tech-stack)
6. [Project Workflow](#6-project-workflow)
7. [Data Cleaning](#7-data-cleaning)
8. [Exploratory Data Analysis](#8-exploratory-data-analysis)
9. [SQL Analysis](#9-sql-analysis)
10. [Tableau Dashboard](#10-tableau-dashboard)
11. [Key Findings](#11-key-findings)
12. [Business Recommendations](#12-business-recommendations)
13. [Project Structure](#13-project-structure)
14. [Quick Start and How to Run](#14-quick-start-and-how-to-run)
15. [KPI Cross-Validation](#15-kpi-cross-validation)
16. [Skills Demonstrated](#16-skills-demonstrated)
17. [License](#17-license)

---

## 1. Overview

This project answers real business questions — *what sells, what is profitable, which
customers and regions matter, and whether discounts actually destroy profit* — using a
clean, reproducible analysis workflow. It is designed to demonstrate practical data
analyst skills: data cleaning, exploratory analysis, SQL, dashboarding and
data-driven storytelling.

## 2. Business Problem

An e-commerce retailer sells office furniture, technology and office supplies across
the United States. Management needs to understand **where money is made and where it is
lost** to improve revenue, profit and margins.

Key questions:

- What products generate the most revenue? Which categories are most profitable?
- Which customers contribute the most revenue? Which customer segments perform best?
- How do sales change over time (seasonality, yearly growth)?
- Which regions and states perform best?
- **Does discounting help or destroy profit?**
- Which products / sub-categories need attention?

## 3. Objectives

1. Clean and standardize the raw transaction data into a trustworthy analysis base.
2. Explore sales, profit, products, customers, geography and discount behaviour.
3. Answer 14 business questions with reproducible Python and SQL analysis.
4. Build an interactive Tableau dashboard with KPIs, trends and filters.
5. Turn the findings into concrete, data-backed business recommendations.

---

## 4. Dataset

**`data/ecommerce_dataset.csv`** — a **synthetic** e-commerce order book generated
programmatically by `python/generate_dataset.py` (fixed random seed, fully reproducible).

| Attribute | Value |
|---|---|
| Records | **5,508** order-line transactions |
| Period | January 2019 – December 2023 (5 years) |
| Products | 120 (3 categories, 17 sub-categories) |
| Customers | 649 |
| Geography | United States — 28 states, 4 regions |
| Origin | **Synthetic / simulated** — contains no real customer data |

**Fields:** `Order ID, Order Date, Customer ID, Customer Name, Segment, Country, State,
City, Region, Product ID, Product Name, Category, Sub-Category, Sales, Quantity,
Discount, Profit, Shipping Cost, Shipping Mode, Payment Mode`

> **Note:** all names, values and addresses are fabricated. The dataset is intentionally
> realistic in *structure and behaviour* (seasonality, discount-driven losses, category
> margin differences) so the analysis is meaningful, but it contains no real personal or
> business information.

## 5. Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11 | Analysis engine |
| Pandas / NumPy | Data wrangling, aggregation, derived fields |
| Matplotlib / Seaborn | Charts and visualizations |
| MySQL 8.0 | Relational SQL analysis |
| Tableau Desktop | Interactive dashboard |
| Excel | Quick exploration of the CSVs |
| Git / GitHub | Version control & portfolio hosting |

---

## 6. Project Workflow

```
data/ecommerce_dataset.csv (raw)
        │
        ▼
python/data_cleaning.py        ──►  outputs/cleaned_data/ecommerce_clean.csv
                                         + data_cleaning_report.txt
        │
        ▼
notebooks/ECommerce_Analysis.ipynb   (EDA + charts)
        │
        ├──► outputs/charts/*.png    (15 charts)
        ▼
sql/ecommerce_analysis.sql           (MySQL analysis)
        ▼
dashboard/Ecommerce_Dashboard.twb    (Tableau dashboard)
        ▼
README ──►  Business Insights & Recommendations
```

---

## 7. Data Cleaning

`python/data_cleaning.py` runs an **11-step, fully logged pipeline**. Every decision is
recorded in **`outputs/cleaned_data/data_cleaning_report.txt`**.

| Step | Action | Result |
|---|---|---|
| 1–2 | Load + inspect types / shape | 5,508 rows × 20 columns |
| 3–4 | Missing values | 27 `Shipping Cost` cells (0.49%) imputed with the median |
| 5 | Duplicate orders | 8 fully-duplicated rows removed |
| 6 | Date conversion | `Order Date` → datetime (validated 2019–2023) |
| 7 | Numeric validation | `Sales, Quantity, Discount, Profit, Shipping Cost` coerced to numeric |
| 8 | Invalid values | 0 invalid rows; **614 negative-profit orders kept** (legitimate losses) |
| 9 | Categorical consistency | Standardized casing (`UPI`, `Cash on Delivery`, etc.) |
| 10 | Derived columns | `Year, Month, Quarter, Order Year-Month, Profit Margin (%)` |
| 11 | Save | **5,500 rows × 25 columns** |

**Cleaning decisions:** missing numeric data is imputed with the median (robust to
outliers); loss-making orders are *not* removed because they are valid business
observations that drive the discount analysis.

---

## 8. Exploratory Data Analysis

The complete EDA lives in **`notebooks/ECommerce_Analysis.ipynb`** (28 executed code
cells, 0 errors) and covers:

- **Sales analysis** — KPIs, monthly & yearly trends, YoY growth
- **Product analysis** — top / bottom products, categories, sub-categories
- **Customer analysis** — top customers, segments, order value
- **Geographic analysis** — region / state / city performance
- **Discount analysis** — distribution, discount vs profit, loss rates
- **Seasonality** — year × month sales heatmap
- **Business questions** — all 14 answered with code (no hardcoded results)

All **15 charts** are saved to **`outputs/charts/`** with meaningful titles and labels.

---

## 9. SQL Analysis

**`sql/ecommerce_analysis.sql`** contains **33 professional MySQL queries** covering
total KPIs, monthly / yearly trends, category & sub-category performance, top / bottom
products, top customers, region / state / segment performance, discount vs profit and
profit margins.

Techniques demonstrated:

- `SELECT`, `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`
- `CASE` expressions (discount buckets, performance tiers, customer tiers)
- Aggregate functions (`SUM`, `COUNT`, `AVG`, `ROUND`)
- `JOIN` (self-joins on aggregate subqueries)
- CTEs (`WITH ... AS`)
- Subqueries (correlated & scalar)
- Window functions (`LAG`, `RANK`, `ROW_NUMBER`, `SUM() OVER ()`)

All queries were **validated by execution** against the real dataset; every result
matches the Python and Tableau numbers (see [KPI Cross-Validation](#15-kpi-cross-validation)).

---

## 10. Tableau Dashboard

**`dashboard/Ecommerce_Dashboard.twb`** — *"E-Commerce Analytics Dashboard"*, an
interactive workbook connected to the cleaned CSV.

- **6 KPI cards:** Total Sales · Total Profit · Total Orders · Total Quantity ·
  Average Order Value · Profit Margin
- **10 visualizations:** Monthly Sales & Profit Trends, Sales / Profit by Category,
  Sales by Region, Top 10 Products, Bottom 10 by Profit, Sales by Segment,
  Discount vs Profit, Geographic Sales Analysis (map-ready `State` field)
- **8 interactive quick filters:** Year · Month · Category · Sub-Category · Region ·
  Segment · Customer · Product

> Open `Ecommerce_Dashboard.twb` in **Tableau Desktop (2021.2+)**. If the connection
> breaks after moving the project, re-point it via **Data → Edit Connection** to
> `outputs/cleaned_data/ecommerce_clean.csv`.

---

## 11. Key Findings

All numbers come straight from the executed notebook and SQL (cross-validated).

| KPI | Value |
|---|---|
| Total Sales | **$4,310,325** |
| Total Profit | **$589,096** |
| Total Orders | 5,500 |
| Total Quantity | 18,051 |
| Average Order Value | **$783.70** |
| Overall Profit Margin | **13.7%** |

**1. Technology is the revenue and profit engine.** It contributes **50.8%** of sales
($2.19M) and **60.5%** of profit at a 16.3% margin. Office Supplies contributes the
least revenue (18.9%) but a healthy 15.8% margin.

**2. Furniture is the weak link.** Furniture makes 30.3% of sales ($1.31M) but only
**8.0% margin** — the lowest of any category. Sub-categories `Bookcases` (7.4%),
`Chairs` (7.7%) and `Tables` (8.4%) have the worst margins in the business.

**3. Discounts destroy profit.** Discount and profit margin are **strongly negatively
correlated (−0.74)**. Loss-making orders rise from **0%** (no discount) → **2.6%**
(≤20%) → **21.7%** (20–40%) → **53.3%** (40%+). Orders discounted 40%+ are loss-making
on average (**−5.9% margin**).

**4. Clear seasonality.** Sales peak in **November** ($474K) and December, with
October–December the strongest quarter. Sales dipped through 2021–2022 and rebounded
**+14.7% in 2023**.

**5. Best-performing geography.** The **Central** region leads revenue ($1.13M); the
**West** is the most profitable region (14.4% margin). The **South** trails on both
revenue and margin.

**6. High-value customers and segments.** **Consumer** is the largest segment (50% of
customers, 51.6% of revenue). **Corporate** has the best margin (14.1%). Top customer
`Isabella Morris` alone generates **$24,276**. All 649 customers are repeat buyers.

**7. Star vs. low-value products.** `Nova Copiers 963` tops both sales ($189K) and
profit ($30.2K). Low-value SKUs such as Fasteners, Labels and Envelopes each generate
under ~$400 of total profit and are candidates for bundling or delisting.

---

## 12. Business Recommendations

1. **Tame furniture discounts.** Re-price Furniture (esp. Chairs, Bookcases, Tables)
   and cap discounts at ~20%; the 40%+ discount tier is loss-making across the store.
2. **Invest in Technology.** It drives revenue *and* profit — allocate marketing budget,
   bundle accessories and stock Copiers / Phones ahead of Q4.
3. **Fix the South.** It underperforms in both revenue and margin; investigate pricing,
   shipping cost and assortment before assuming it is a market issue.
4. **Exploit seasonality.** Plan inventory and promotions for Oct–Dec (peak = November);
   use slower months (Jan–Feb) for clearances at controlled discounts.
5. **Model West success.** The West converts similar sales volume into the best margins —
   replicate its category mix and discount discipline in other regions.
6. **Grow B2B.** Corporate is the highest-margin segment — build account management and
   corporate pricing programs.
7. **Retain top customers.** Tier customers (Platinum / Gold / Silver) and reward the
   top ~200 customers (≈ half of revenue) with loyalty programs.
8. **Rationalise the tail.** Bundle or delist Fasteners, Labels and Envelopes that add
   operational cost without meaningful profit.

> Every recommendation above is supported by the analysis — see the cleaning report in
> `outputs/cleaned_data/`, the executed notebook and the SQL outputs for the numbers.

---

## 13. Project Structure

```
E-Commerce-Analytics/
│
├── data/
│   └── ecommerce_dataset.csv            # Raw synthetic dataset (5,508 records)
│
├── notebooks/
│   └── ECommerce_Analysis.ipynb         # Full EDA (executed, 0 errors)
│
├── python/
│   ├── generate_dataset.py              # Reproducible synthetic dataset generator
│   ├── data_cleaning.py                 # 11-step cleaning pipeline
│   ├── build_notebook.py                # Builds the EDA notebook programmatically
│   └── build_tableau_twb.py             # Builds the Tableau workbook programmatically
│
├── sql/
│   └── ecommerce_analysis.sql           # 33 validated MySQL queries
│
├── dashboard/
│   └── Ecommerce_Dashboard.twb          # Tableau dashboard (16 worksheets + filters)
│
├── outputs/
│   ├── charts/                          # 15 EDA charts (PNG)
│   └── cleaned_data/
│       ├── ecommerce_clean.csv          # Cleaned dataset (5,500 × 25)
│       └── data_cleaning_report.txt     # Cleaning log & decisions
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 14. Quick Start and How to Run

### Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Running scripts & notebook |
| pip | any recent | Installing dependencies |
| MySQL | 8.0+ | SQL analysis (optional) |
| Tableau Desktop | 2021.2+ | Dashboard (optional) |

### Step 1 — Clone the repository

```bash
git clone https://github.com/SumanthBandla/E-Commerce-Analytics.git
cd E-Commerce-Analytics
```

### Step 2 — Set up a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Generate the dataset (optional)

The dataset is already committed, but it is fully reproducible:

```bash
python python/generate_dataset.py
```

### Step 5 — Run data cleaning

Regenerates `outputs/cleaned_data/ecommerce_clean.csv` and the cleaning report:

```bash
python python/data_cleaning.py
```

### Step 6 — Run the EDA notebook

```bash
jupyter notebook notebooks/ECommerce_Analysis.ipynb
```

or execute it headlessly to regenerate all charts in `outputs/charts/`:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/ECommerce_Analysis.ipynb
```

### Step 7 — Run the SQL analysis (MySQL)

1. Execute the top of `sql/ecommerce_analysis.sql` to create the database and table.
2. Uncomment the `LOAD DATA LOCAL INFILE` line to import
   `outputs/cleaned_data/ecommerce_clean.csv`.
3. Run the 33 analysis queries — all results match the Python notebook.

### Step 8 — Open the Tableau dashboard

Open `dashboard/Ecommerce_Dashboard.twb` in **Tableau Desktop**. If the connection
breaks, re-point it to `outputs/cleaned_data/ecommerce_clean.csv` via
**Data → Edit Connection**.

---

## 15. KPI Cross-Validation

The same KPIs are computed three independent ways and match exactly:

| KPI | Python (notebook) | SQL (query) | Tableau |
|---|---|---|---|
| Total Sales | $4,310,325 | $4,310,324.74 | Total Sales KPI card |
| Total Profit | $589,096 | $589,095.65 | Total Profit KPI card |
| Total Orders | 5,500 | 5,500 | Total Orders KPI card |
| Average Order Value | $783.70 | $783.70 | AOV KPI card |
| Best Category (Revenue) | Technology | Technology | Sales by Category |
| Peak Month | Month 11 | Month 11 | Monthly Sales Trend |

---

## 16. Skills Demonstrated

- Python for data analysis (Pandas, NumPy, Matplotlib, Seaborn)
- Data cleaning, validation and reproducibility
- Exploratory data analysis & statistical reasoning
- SQL: aggregation, window functions, CTEs, subqueries, joins
- Dashboard design with Tableau (KPIs, filters, visual analytics)
- Data storytelling & business recommendations
- Version control with Git / GitHub, project documentation

---

## 17. License

This is an educational portfolio project. The dataset is fully synthetic. Feel free to
clone, modify and use it as a learning resource or portfolio sample.
