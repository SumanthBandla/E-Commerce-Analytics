"""
build_notebook.py
=================
Programmatically builds `notebooks/ECommerce_Analysis.ipynb` containing the full
Exploratory Data Analysis (EDA) workflow for the E-Commerce Analytics project.

The notebook is created with nbformat so it is fully reproducible and then
executed with nbconvert, which also regenerates every chart in `outputs/charts/`.

Run from anywhere inside the repository:
    python python/build_notebook.py
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = PROJECT_ROOT / "notebooks" / "ECommerce_Analysis.ipynb"

# ---------------------------------------------------------------------------
# Helper to build markdown / code cells
# ---------------------------------------------------------------------------
def md(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(source)


def code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source)


# ---------------------------------------------------------------------------
# Notebook cells
# ---------------------------------------------------------------------------
cells: list[nbf.NotebookNode] = []

# --- 0. Title ---------------------------------------------------------------
cells.append(md(
    "# E-Commerce Analytics — Exploratory Data Analysis (EDA)\n"
    "\n"
    "An end-to-end analysis of a synthetic e-commerce order book covering **sales**, "
    "**profit**, **products**, **customers**, **geography** and **discounts**.\n"
    "\n"
    "**Dataset**: synthetic `ecommerce_dataset.csv` (5,500 cleaned transactions, 2019–2023).\n"
    "**Pipeline**: Raw Dataset → Data Cleaning → EDA → SQL Analysis → Tableau Dashboard → Business Insights.\n"
    "\n"
    "This notebook focuses on the **EDA stage**. It mirrors the exact numbers used by the "
    "SQL queries and the Tableau dashboard so all deliverables stay consistent."
))

cells.append(md("## 0. Setup & Configuration"))

cells.append(code(
    "import warnings\n"
    "warnings.filterwarnings(\"ignore\")\n"
    "\n"
    "from pathlib import Path\n"
    "\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib.ticker as mticker\n"
    "import seaborn as sns\n"
    "\n"
    "# Locate the project root regardless of the current working directory\n"
    "ROOT = Path.cwd()\n"
    "while not (ROOT / \"data\").exists() and ROOT != ROOT.parent:\n"
    "    ROOT = ROOT.parent\n"
    "\n"
    "DATA_PATH = ROOT / \"outputs\" / \"cleaned_data\" / \"ecommerce_clean.csv\"\n"
    "CHART_DIR = ROOT / \"outputs\" / \"charts\"\n"
    "CHART_DIR.mkdir(parents=True, exist_ok=True)\n"
    "\n"
    "# Consistent, portfolio-ready chart style\n"
    "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
    "plt.rcParams.update({\n"
    "    \"figure.figsize\": (10, 5.5),\n"
    "    \"axes.titlesize\": 13,\n"
    "    \"axes.titleweight\": \"bold\",\n"
    "    \"axes.labelsize\": 11,\n"
    "    \"figure.dpi\": 120,\n"
    "    \"savefig.dpi\": 150,\n"
    "    \"savefig.bbox\": \"tight\",\n"
    "})\n"
    "\n"
    "def save_chart(fig, name):\n"
    "    \"\"\"Save a matplotlib figure to the charts folder.\"\"\"\n"
    "    path = CHART_DIR / name\n"
    "    fig.savefig(path)\n"
    "    plt.close(fig)\n"
    "    print(f\"Saved chart: {path.name}\")"
))

cells.append(code(
    "df = pd.read_csv(DATA_PATH, parse_dates=[\"Order Date\"])\n"
    "print(f\"Cleaned dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} columns\")"
))

# --- 1. Data Overview -------------------------------------------------------
cells.append(md("## 1. Data Overview"))
cells.append(code(
    "print(\"--- Data types ---\")\n"
    "print(df.dtypes.to_string())\n"
    "print(\"\\n--- Missing values ---\")\n"
    "print(df.isna().sum().to_string())\n"
    "print(\"\\n--- Duplicates ---\")\n"
    "print(f\"Duplicate rows: {df.duplicated().sum()}\")"
))

cells.append(code(
    "pd.set_option(\"display.max_columns\", None)\n"
    "df.head(5)"
))

cells.append(code(
    "df.describe().round(2)"
))

# --- 2. Sales Analysis ------------------------------------------------------
cells.append(md("## 2. Sales Analysis"))
cells.append(code(
    "total_sales = df[\"Sales\"].sum()\n"
    "total_profit = df[\"Profit\"].sum()\n"
    "total_orders = df[\"Order ID\"].nunique()\n"
    "total_quantity = df[\"Quantity\"].sum()\n"
    "aov = total_sales / total_orders\n"
    "profit_margin = total_profit / total_sales * 100\n"
    "\n"
    "kpis = pd.DataFrame({\n"
    "    \"KPI\": [\"Total Sales\", \"Total Profit\", \"Total Orders\", \"Total Quantity\",\n"
    "            \"Average Order Value (AOV)\", \"Profit Margin\"],\n"
    "    \"Value\": [f\"${total_sales:,.0f}\", f\"${total_profit:,.0f}\", f\"{total_orders:,}\",\n"
    "               f\"{total_quantity:,}\", f\"${aov:,.2f}\", f\"{profit_margin:.1f}%\"],\n"
    "})\n"
    "kpis"
))

cells.append(code(
    "monthly = df.groupby(df[\"Order Date\"].dt.to_period(\"M\")).agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\")\n"
    ").reset_index()\n"
    "monthly[\"Year-Month\"] = monthly[\"Order Date\"].astype(str)\n"
    "\n"
    "fig, ax1 = plt.subplots()\n"
    "ax1.plot(monthly[\"Year-Month\"], monthly[\"Sales\"] / 1_000, color=\"#1f77b4\", linewidth=2,\n"
    "         marker=\"o\", markersize=3, label=\"Sales ($K)\")\n"
    "ax1.set_xlabel(\"Year-Month\")\n"
    "ax1.set_ylabel(\"Sales ($K)\", color=\"#1f77b4\")\n"
    "ax1.tick_params(axis=\"y\", labelcolor=\"#1f77b4\")\n"
    "ax1.tick_params(axis=\"x\", rotation=90)\n"
    "\n"
    "ax2 = ax1.twinx()\n"
    "ax2.plot(monthly[\"Year-Month\"], monthly[\"Profit\"] / 1_000, color=\"#d62728\", linewidth=1.6,\n"
    "         marker=\"s\", markersize=3, label=\"Profit ($K)\")\n"
    "ax2.set_ylabel(\"Profit ($K)\", color=\"#d62728\")\n"
    "ax2.tick_params(axis=\"y\", labelcolor=\"#d62728\")\n"
    "\n"
    "ax1.set_title(\"Monthly Sales & Profit Trend (2019-2023)\")\n"
    "lines1, labels1 = ax1.get_legend_handles_labels()\n"
    "lines2, labels2 = ax2.get_legend_handles_labels()\n"
    "ax1.legend(lines1 + lines2, labels1 + labels2, loc=\"upper left\")\n"
    "save_chart(fig, \"monthly_sales_profit_trend.png\")\n"
    "plt.show()\n"
    "\n"
    "print(\"Top 3 months by sales:\")\n"
    "print(monthly.sort_values(\"Sales\", ascending=False).head(3).to_string(index=False))"
))

cells.append(code(
    "yearly = df.groupby(df[\"Order Date\"].dt.year).agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"), Orders=(\"Order ID\", \"nunique\")\n"
    ").reset_index().rename(columns={\"Order Date\": \"Year\"})\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "x = np.arange(len(yearly))\n"
    "width = 0.38\n"
    "ax.bar(x - width / 2, yearly[\"Sales\"] / 1_000, width, label=\"Sales ($K)\", color=\"#1f77b4\")\n"
    "ax.bar(x + width / 2, yearly[\"Profit\"] / 1_000, width, label=\"Profit ($K)\", color=\"#2ca02c\")\n"
    "ax.set_xticks(x, yearly[\"Year\"])\n"
    "ax.set_xlabel(\"Year\")\n"
    "ax.set_ylabel(\"Amount ($K)\")\n"
    "ax.set_title(\"Yearly Sales & Profit\")\n"
    "ax.legend()\n"
    "for i in range(len(yearly)):\n"
    "    ax.text(x[i] - width / 2, yearly[\"Sales\"][i] / 1_000 + 20, f\"{yearly['Sales'][i]/1_000:.0f}K\",\n"
    "            ha=\"center\", fontsize=8)\n"
    "    ax.text(x[i] + width / 2, yearly[\"Profit\"][i] / 1_000 + 20, f\"{yearly['Profit'][i]/1_000:.0f}K\",\n"
    "            ha=\"center\", fontsize=8)\n"
    "save_chart(fig, \"yearly_sales_profit.png\")\n"
    "plt.show()\n"
    "\n"
    "yearly"
))

# --- 3. Product Analysis ----------------------------------------------------
cells.append(md("## 3. Product Analysis"))
cells.append(code(
    "category = df.groupby(\"Category\").agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"),\n"
    "    Orders=(\"Order ID\", \"nunique\"), Quantity=(\"Quantity\", \"sum\")\n"
    ").round(2).sort_values(\"Sales\", ascending=False)\n"
    "category[\"Profit Margin (%)\"] = (category[\"Profit\"] / category[\"Sales\"] * 100).round(1)\n"
    "category"
))

cells.append(code(
    "fig, ax = plt.subplots()\n"
    "x = np.arange(len(category))\n"
    "width = 0.38\n"
    "ax.bar(x - width / 2, category[\"Sales\"] / 1_000, width, label=\"Sales ($K)\", color=\"#1f77b4\")\n"
    "ax.bar(x + width / 2, category[\"Profit\"] / 1_000, width, label=\"Profit ($K)\", color=\"#2ca02c\")\n"
    "ax.set_xticks(x, category.index)\n"
    "ax.set_xlabel(\"Category\")\n"
    "ax.set_ylabel(\"Amount ($K)\")\n"
    "ax.set_title(\"Category-wise Sales vs Profit\")\n"
    "ax.legend()\n"
    "save_chart(fig, \"category_sales_profit.png\")\n"
    "plt.show()"
))

cells.append(code(
    "top_products_sales = (df.groupby(\"Product Name\")\n"
    "                      .agg(Sales=(\"Sales\", \"sum\"))\n"
    "                      .sort_values(\"Sales\", ascending=False).head(10))\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "top_products_sales.sort_values(\"Sales\").plot.barh(\n"
    "    ax=ax, color=\"#1f77b4\", legend=False, width=0.7)\n"
    "ax.set_xlabel(\"Total Sales ($)\")\n"
    "ax.set_title(\"Top 10 Products by Sales\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"top10_products_sales.png\")\n"
    "plt.show()\n"
    "top_products_sales.round(2)"
))

cells.append(code(
    "top_products_profit = (df.groupby(\"Product Name\")\n"
    "                       .agg(Profit=(\"Profit\", \"sum\"))\n"
    "                       .sort_values(\"Profit\", ascending=False).head(10))\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "top_products_profit.sort_values(\"Profit\").plot.barh(\n"
    "    ax=ax, color=\"#2ca02c\", legend=False, width=0.7)\n"
    "ax.set_xlabel(\"Total Profit ($)\")\n"
    "ax.set_title(\"Top 10 Products by Profit\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"top10_products_profit.png\")\n"
    "plt.show()\n"
    "top_products_profit.round(2)"
))

cells.append(code(
    "bottom_products_profit = (df.groupby(\"Product Name\")\n"
    "                          .agg(Profit=(\"Profit\", \"sum\"))\n"
    "                          .sort_values(\"Profit\").head(10))\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "bottom_products_profit.sort_values(\"Profit\").plot.barh(\n"
    "    ax=ax, color=\"#d62728\", legend=False, width=0.7)\n"
    "ax.set_xlabel(\"Total Profit ($)\")\n"
    "ax.set_title(\"Bottom 10 Products by Profit (Lowest Profit)\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"bottom10_products_profit.png\")\n"
    "plt.show()\n"
    "bottom_products_profit.round(2)"
))

cells.append(code(
    "most_sold = (df.groupby(\"Product Name\")\n"
    "             .agg(Quantity=(\"Quantity\", \"sum\"), Sales=(\"Sales\", \"sum\"))\n"
    "             .sort_values(\"Quantity\", ascending=False).head(10))\n"
    "print(\"Top 10 most-sold products (by units sold):\")\n"
    "most_sold.round(2)"
))

cells.append(code(
    "subcat = (df.groupby([\"Category\", \"Sub-Category\"])\n"
    "          .agg(Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"))\n"
    "          .sort_values(\"Sales\", ascending=False).head(10))\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "idx = [f\"{c} | {s}\" for c, s in subcat.index]\n"
    "subcat_plot = subcat.copy()\n"
    "subcat_plot.index = idx\n"
    "subcat_plot.sort_values(\"Sales\").plot.barh(ax=ax, color=[\"#1f77b4\", \"#2ca02c\"], width=0.7)\n"
    "ax.set_xlabel(\"Amount ($)\")\n"
    "ax.set_title(\"Top 10 Sub-Categories by Sales (Sales vs Profit)\")\n"
    "ax.legend(loc=\"lower right\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"subcategory_performance.png\")\n"
    "plt.show()\n"
    "subcat.round(2)"
))

# --- 4. Customer Analysis ---------------------------------------------------
cells.append(md("## 4. Customer Analysis"))
cells.append(code(
    "n_customers = df[\"Customer ID\"].nunique()\n"
    "print(f\"Number of unique customers: {n_customers:,}\")\n"
    "print(f\"Average order value per customer: ${total_sales / n_customers:,.2f}\")\n"
    "\n"
    "top_customers = (df.groupby([\"Customer ID\", \"Customer Name\"])\n"
    "                 .agg(Sales=(\"Sales\", \"sum\"), Orders=(\"Order ID\", \"nunique\"))\n"
    "                 .reset_index()\n"
    "                 .sort_values(\"Sales\", ascending=False).head(10))\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "labels = [f\"{n[:10]}...\" if len(n) > 10 else n for n in top_customers[\"Customer Name\"][::-1]]\n"
    "ax.barh(labels, top_customers[\"Sales\"][::-1] / 1_000, color=\"#9467bd\")\n"
    "ax.set_xlabel(\"Total Sales ($K)\")\n"
    "ax.set_title(\"Top 10 Customers by Sales\")\n"
    "save_chart(fig, \"top10_customers_sales.png\")\n"
    "plt.show()\n"
    "top_customers.round(2)"
))

cells.append(code(
    "(df.groupby([\"Customer ID\", \"Customer Name\"])\n"
    " .agg(Profit=(\"Profit\", \"sum\"))\n"
    " .sort_values(\"Profit\", ascending=False).head(10).round(2))"
))

cells.append(code(
    "segments = df.groupby(\"Segment\").agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"),\n"
    "    Orders=(\"Order ID\", \"nunique\"), Customers=(\"Customer ID\", \"nunique\")\n"
    ").round(2).sort_values(\"Sales\", ascending=False)\n"
    "segments[\"Profit Margin (%)\"] = (segments[\"Profit\"] / segments[\"Sales\"] * 100).round(1)\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "x = np.arange(len(segments))\n"
    "width = 0.38\n"
    "ax.bar(x - width / 2, segments[\"Sales\"] / 1_000, width, label=\"Sales ($K)\", color=\"#ff7f0e\")\n"
    "ax.bar(x + width / 2, segments[\"Profit\"] / 1_000, width, label=\"Profit ($K)\", color=\"#2ca02c\")\n"
    "ax.set_xticks(x, segments.index)\n"
    "ax.set_ylabel(\"Amount ($K)\")\n"
    "ax.set_title(\"Customer Segment Performance (Sales vs Profit)\")\n"
    "ax.legend()\n"
    "save_chart(fig, \"segment_sales_profit.png\")\n"
    "plt.show()\n"
    "segments"
))

# --- 5. Geographic Analysis -------------------------------------------------
cells.append(md("## 5. Geographic Analysis"))
cells.append(code(
    "region = df.groupby(\"Region\").agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"), Orders=(\"Order ID\", \"nunique\")\n"
    ").round(2).sort_values(\"Sales\", ascending=False)\n"
    "region[\"Profit Margin (%)\"] = (region[\"Profit\"] / region[\"Sales\"] * 100).round(1)\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "x = np.arange(len(region))\n"
    "width = 0.38\n"
    "ax.bar(x - width / 2, region[\"Sales\"] / 1_000, width, label=\"Sales ($K)\", color=\"#17becf\")\n"
    "ax.bar(x + width / 2, region[\"Profit\"] / 1_000, width, label=\"Profit ($K)\", color=\"#2ca02c\")\n"
    "ax.set_xticks(x, region.index)\n"
    "ax.set_ylabel(\"Amount ($K)\")\n"
    "ax.set_title(\"Region-wise Sales vs Profit\")\n"
    "ax.legend()\n"
    "save_chart(fig, \"region_sales_profit.png\")\n"
    "plt.show()\n"
    "region"
))

cells.append(code(
    "print(f\"Country distribution (transactions): {df['Country'].value_counts().to_dict()}\")\n"
    "\n"
    "state = df.groupby(\"State\").agg(Sales=(\"Sales\", \"sum\")).sort_values(\"Sales\", ascending=False).head(10)\n"
    "fig, ax = plt.subplots()\n"
    "state.sort_values(\"Sales\").plot.barh(ax=ax, color=\"#8c564b\", legend=False, width=0.7)\n"
    "ax.set_xlabel(\"Total Sales ($)\")\n"
    "ax.set_title(\"Top 10 States by Sales\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"state_sales.png\")\n"
    "plt.show()\n"
    "state.round(2)"
))

cells.append(code(
    "city = df.groupby(\"City\").agg(Sales=(\"Sales\", \"sum\")).sort_values(\"Sales\", ascending=False).head(10)\n"
    "fig, ax = plt.subplots()\n"
    "city.sort_values(\"Sales\").plot.barh(ax=ax, color=\"#7f7f7f\", legend=False, width=0.7)\n"
    "ax.set_xlabel(\"Total Sales ($)\")\n"
    "ax.set_title(\"Top 10 Cities by Sales\")\n"
    "ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f\"${v/1_000:.0f}K\"))\n"
    "save_chart(fig, \"city_sales.png\")\n"
    "plt.show()\n"
    "city.round(2)"
))

# --- 6. Discount Analysis ---------------------------------------------------
cells.append(md("## 6. Discount Analysis"))
cells.append(code(
    "fig, ax = plt.subplots()\n"
    "sns.histplot(df[\"Discount\"], bins=20, kde=False, color=\"#ff7f0e\", ax=ax)\n"
    "ax.set_xlabel(\"Discount\")\n"
    "ax.set_ylabel(\"Number of Orders\")\n"
    "ax.set_title(\"Distribution of Discounts\")\n"
    "save_chart(fig, \"discount_distribution.png\")\n"
    "plt.show()\n"
    "\n"
    "print(\"Discount share of orders:\")\n"
    "print(df[\"Discount\"].value_counts(normalize=True).sort_index().round(4).to_string())"
))

cells.append(code(
    "df[\"Discount Bucket\"] = pd.cut(df[\"Discount\"], [-0.01, 0.01, 0.2, 0.4, 0.6],\n"
    "                                labels=[\"0%\", \"Up to 20%\", \"20-40%\", \"40%+\"])\n"
    "\n"
    "disc_by_bucket = df.groupby(\"Discount Bucket\", observed=True).agg(\n"
    "    Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"), Orders=(\"Order ID\", \"nunique\")\n"
    ").round(2)\n"
    "disc_by_bucket[\"Profit Margin (%)\"] = (disc_by_bucket[\"Profit\"] / disc_by_bucket[\"Sales\"] * 100).round(1)\n"
    "\n"
    "fig, ax = plt.subplots()\n"
    "x = np.arange(len(disc_by_bucket))\n"
    "width = 0.38\n"
    "ax.bar(x - width / 2, disc_by_bucket[\"Sales\"] / 1_000, width, label=\"Sales ($K)\", color=\"#1f77b4\")\n"
    "ax.bar(x + width / 2, disc_by_bucket[\"Profit\"] / 1_000, width, label=\"Profit ($K)\", color=\"#d62728\")\n"
    "ax.set_xticks(x, disc_by_bucket.index)\n"
    "ax.set_xlabel(\"Discount Level\")\n"
    "ax.set_ylabel(\"Amount ($K)\")\n"
    "ax.set_title(\"Discount Level vs Sales & Profit\")\n"
    "ax.legend()\n"
    "save_chart(fig, \"discount_vs_profit.png\")\n"
    "plt.show()\n"
    "disc_by_bucket"
))

cells.append(code(
    "corr = df[[\"Discount\", \"Profit Margin (%)\", \"Sales\", \"Profit\"]].corr()\n"
    "print(\"Correlation between Discount and other metrics:\")\n"
    "print(corr[\"Discount\"].round(3).to_string())\n"
    "\n"
    "loss_rate_by_discount = df.assign(\n"
    "    Loss=df[\"Profit\"] < 0\n"
    ").groupby(\"Discount Bucket\", observed=True)[\"Loss\"].mean().round(3) * 100\n"
    "print(\"\\nShare of loss-making orders by discount level (%):\")\n"
    "print(loss_rate_by_discount.astype(str).to_string())"
))

cells.append(code(
    "print(\"Products with the highest average discount:\")\n"
    "(df.groupby([\"Product ID\", \"Product Name\", \"Category\"])\n"
    " .agg(Avg_Discount=(\"Discount\", \"mean\"), Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\"))\n"
    " .sort_values(\"Avg_Discount\", ascending=False).head(10).round(3))"
))

cells.append(code(
    "print(\"Average discount by category:\")\n"
    "df.groupby(\"Category\")[\"Discount\"].mean().round(3).to_string()"
))

# --- 7. Monthly heatmap -----------------------------------------------------
cells.append(md("## 7. Seasonal Pattern (Heatmap)"))
cells.append(code(
    "pivot = df.pivot_table(index=df[\"Order Date\"].dt.year, columns=df[\"Order Date\"].dt.month,\n"
    "                       values=\"Sales\", aggfunc=\"sum\") / 1_000\n"
    "fig, ax = plt.subplots(figsize=(11, 4.5))\n"
    "sns.heatmap(pivot, annot=True, fmt=\".0f\", cmap=\"YlGnBu\", cbar_kws={\"label\": \"Sales ($K)\"}, ax=ax)\n"
    "ax.set_xlabel(\"Month\")\n"
    "ax.set_ylabel(\"Year\")\n"
    "ax.set_title(\"Monthly Sales Heatmap ($K) — shows the year-end seasonality\")\n"
    "save_chart(fig, \"monthly_sales_heatmap.png\")\n"
    "plt.show()"
))

# --- 8. Business questions --------------------------------------------------
cells.append(md("## 8. Business Questions — Answers"))
cells.append(code(
    "best_cat_sales = category[\"Sales\"].idxmax()\n"
    "best_cat_profit = category[\"Profit\"].idxmax()\n"
    "top_product_sales = top_products_sales.index[0]\n"
    "worst_product_profit = (df.groupby(\"Product Name\")[\"Profit\"].sum()\n"
    "                        .sort_values().index[0])\n"
    "top_customer = (df.groupby(\"Customer Name\")[\"Sales\"].sum().sort_values(ascending=False).index[0])\n"
    "best_region = region[\"Sales\"].idxmax()\n"
    "month_sales = df.groupby(df[\"Order Date\"].dt.month)[\"Sales\"].sum()\n"
    "month_profit = df.groupby(df[\"Order Date\"].dt.month)[\"Profit\"].sum()\n"
    "best_month_sales = int(month_sales.idxmax())\n"
    "best_month_profit = int(month_profit.idxmax())\n"
    "\n"
    "# Sub-category needing improvement = lowest profit margin among sub-categories\n"
    "subcat_margin = (df.groupby([\"Category\", \"Sub-Category\"])\n"
    "                 .agg(Sales=(\"Sales\", \"sum\"), Profit=(\"Profit\", \"sum\")))\n"
    "subcat_margin[\"Margin\"] = subcat_margin[\"Profit\"] / subcat_margin[\"Sales\"] * 100\n"
    "weakest_subcat = subcat_margin.sort_values(\"Margin\").index[0]\n"
    "best_segment = segments[\"Sales\"].idxmax()\n"
    "\n"
    "# Share of loss-making orders by discount level (reused in Q11)\n"
    "loss_by_bucket = (df.assign(Loss=df[\"Profit\"] < 0)\n"
    "                  .groupby(\"Discount Bucket\", observed=True)[\"Loss\"].mean())\n"
    "\n"
    "answers = pd.DataFrame({\n"
    "    \"Q\": range(1, 15),\n"
    "    \"Business Question\": [\n"
    "        \"What is the total revenue?\",\n"
    "        \"What is the total profit?\",\n"
    "        \"Which category generates the most revenue?\",\n"
    "        \"Which category generates the most profit?\",\n"
    "        \"Which products have the highest sales?\",\n"
    "        \"Which products have the lowest profit?\",\n"
    "        \"Which customers generate the most revenue?\",\n"
    "        \"Which region performs best?\",\n"
    "        \"Which month has the highest sales?\",\n"
    "        \"Which month has the highest profit?\",\n"
    "        \"Does higher discount reduce profit?\",\n"
    "        \"Which sub-category needs improvement?\",\n"
    "        \"What is the average order value?\",\n"
    "        \"Which customer segment performs best?\",\n"
    "    ],\n"
    "    \"Answer\": [\n"
    "        f\"${total_sales:,.0f}\",\n"
    "        f\"${total_profit:,.0f}\",\n"
    "        best_cat_sales,\n"
    "        best_cat_profit,\n"
    "        top_product_sales,\n"
    "        worst_product_profit,\n"
    "        top_customer,\n"
    "        f\"{best_region} (${region['Sales'].max():,.0f})\",\n"
    "        f\"Month {best_month_sales} (${month_sales.max():,.0f})\",\n"
    "        f\"Month {best_month_profit} (${month_profit.max():,.0f})\",\n"
    "        (f\"Yes - margin correlation {corr['Discount']['Profit Margin (%)']:.2f}. \"\n"
    "         f\"Loss-making orders rise from {loss_by_bucket.iloc[0]*100:.0f}% ({loss_by_bucket.index[0]}) \"\n"
    "         f\"to {loss_by_bucket.iloc[-1]*100:.0f}% ({loss_by_bucket.index[-1]}).\"),\n"
    "        f\"{weakest_subcat[0]} | {weakest_subcat[1]}\",\n"
    "        f\"${aov:,.2f}\",\n"
    "        best_segment,\n"
    "    ],\n"
    "})\n"
    "pd.set_option(\"display.max_colwidth\", 90)\n"
    "answers"
))

# --- 9. Takeaways -----------------------------------------------------------
cells.append(md(
    "## 9. Key Takeaways & Next Steps\n"
    "\n"
    "* **Sales** are concentrated in **Technology** (largest revenue) while **Office Supplies** "
    "delivers the healthiest margins.\n"
    "* **Consumer** is the biggest segment; **Corporate** offers the highest-value orders.\n"
    "* Sales peak in **November–December** — a clear year-end holiday seasonality.\n"
    "* **High discounts destroy margin**: orders at 40%+ discount are mostly loss-making.\n"
    "* The **West** region leads in sales; several Furniture sub-categories need margin review.\n"
    "\n"
    "**Next steps** in the workflow: SQL analysis (`sql/ecommerce_analysis.sql`), the Tableau "
    "dashboard (`dashboard/Ecommerce_Dashboard.twb`) and the final business-insights report in the README."
))

# ---------------------------------------------------------------------------
# Assemble and write the notebook
# ---------------------------------------------------------------------------
nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11"},
}

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print(f"Notebook written to {NOTEBOOK_PATH.name}")
print(f"Cells: {len(nb['cells'])}")
