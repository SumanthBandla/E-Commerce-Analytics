"""
build_tableau_twb.py
====================
Programmatically generates `dashboard/Ecommerce_Dashboard.twb`, a Tableau
Desktop workbook connected to the cleaned dataset.

It creates a data source, the worksheets required by the project brief, six KPI
cards and a dashboard with interactive quick filters.

Note: the file connects to `outputs/cleaned_data/ecommerce_clean.csv` using an
absolute path generated at build time. If the project is moved, re-point the
connection in Tableau (Data > Edit Connection) or re-run this script.

Run from anywhere inside the repository:
    python python/build_tableau_twb.py
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = PROJECT_ROOT / "outputs" / "cleaned_data" / "ecommerce_clean.csv"
TWB_PATH = PROJECT_ROOT / "dashboard" / "Ecommerce_Dashboard.twb"

# ---------------------------------------------------------------------------
# Datasource columns: (name, caption, datatype, role, type, geographic_role)
# ---------------------------------------------------------------------------
DIM_COLS = [
    ("[Order ID]", "Order ID", "string", "nominal", None),
    ("[Order Date]", "Order Date", "datetime", "nominal", None),
    ("[Customer ID]", "Customer ID", "string", "nominal", None),
    ("[Customer Name]", "Customer Name", "string", "nominal", None),
    ("[Segment]", "Segment", "string", "nominal", None),
    ("[Country]", "Country", "string", "nominal", None),
    ("[State]", "State", "string", "nominal", "state"),
    ("[City]", "City", "string", "nominal", "city"),
    ("[Region]", "Region", "string", "nominal", None),
    ("[Product ID]", "Product ID", "string", "nominal", None),
    ("[Product Name]", "Product Name", "string", "nominal", None),
    ("[Category]", "Category", "string", "nominal", None),
    ("[Sub-Category]", "Sub-Category", "string", "nominal", None),
    ("[Shipping Mode]", "Shipping Mode", "string", "nominal", None),
    ("[Payment Mode]", "Payment Mode", "string", "nominal", None),
    ("[Year]", "Year", "integer", "nominal", None),
    ("[Month]", "Month", "integer", "ordinal", None),
    ("[Quarter]", "Quarter", "integer", "ordinal", None),
    ("[Order Year-Month]", "Order Year-Month", "string", "ordinal", None),
]
MEASURE_COLS = [
    ("[Sales]", "Sales", "real", "quantitative"),
    ("[Quantity]", "Quantity", "integer", "quantitative"),
    ("[Discount]", "Discount", "real", "quantitative"),
    ("[Profit]", "Profit", "real", "quantitative"),
    ("[Shipping Cost]", "Shipping Cost", "real", "quantitative"),
    ("[Profit Margin (%)]", "Profit Margin (%)", "real", "quantitative"),
]


def xesc(value: str) -> str:
    """Escape a value for use inside an XML attribute."""
    return (
        value.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


# ---------------------------------------------------------------------------
# Column definitions used in worksheet shelves
# ---------------------------------------------------------------------------
def dim_ref(name: str, datatype: str = "string", type_: str = "nominal") -> str:
    return (
        f"<column datatype='{datatype}' name='{name}' role='dimension' type='{type_}' />"
    )


def measure_ref(name: str, agg: str, datatype: str = "real") -> str:
    return (
        f"<column datatype='{datatype}' name='{agg}([{name}])' "
        f"role='measure' type='quantitative' />"
    )


def dependency(col_name: str, caption: str, datatype: str, type_: str) -> str:
    return (
        f"<column caption='{caption}' datatype='{datatype}' name='{col_name}' "
        f"role='dimension' type='{type_}' />"
    )


def measure_dependency(col_name: str, caption: str, datatype: str) -> str:
    return (
        f"<column caption='{caption}' datatype='{datatype}' name='SUM([{col_name}])' "
        f"role='measure' type='quantitative' />"
    )


# ---------------------------------------------------------------------------
# Worksheet factory
# ---------------------------------------------------------------------------
def worksheet(name: str, deps: list[str], rows: str, cols: str, mark: str = "Automatic") -> str:
    return f"""  <worksheet name='{name}'>
    <table>
      <view>
        <datasources>
          <datasource caption='ecommerce_clean' name='ecommerce_clean' />
        </datasources>
        <datasource-dependencies>
{deps}
        </datasource-dependencies>
        <aggregation>true</aggregation>
        <style>
          <class value='tab' />
          <mark value='Automatic' />
        </style>
        <rows>
{rows}
        </rows>
        <cols>
{cols}
        </cols>
        <panes>
          <pane>
            <view-formats />
            <inner-panes>
              <pane>
                <view-formats />
                <mark class='{mark}' />
              </pane>
            </inner-panes>
          </pane>
        </panes>
      </view>
    </table>
  </worksheet>"""


def ind(text: str, level: int = 2) -> str:
    return "\n".join("  " * level + line if line.strip() else line for line in text.splitlines())


# ---------------------------------------------------------------------------
# Build all worksheets
# ---------------------------------------------------------------------------
ws = []

# --- KPI text cards --------------------------------------------------------
kpis = [
    ("KPI - Total Sales", "[Sales]", "real"),
    ("KPI - Total Profit", "[Profit]", "real"),
    ("KPI - Total Orders", "[Order ID]", "string"),
    ("KPI - Total Quantity", "[Quantity]", "integer"),
    ("KPI - Average Order Value", "[Sales]", "real"),
    ("KPI - Profit Margin", "[Profit Margin (%)]", "real"),
]
for kpi_name, field, dtype in kpis:
    if field == "[Order ID]":
        deps = ["<column caption='Order ID' datatype='string' name='[Order ID]' role='dimension' type='nominal' />"]
        agg = "<column datatype='integer' name='COUNTD([Order ID])' role='measure' type='quantitative' />"
        val = "COUNTD([Order ID])"
    elif field == "[Profit Margin (%)]":
        deps = [measure_dependency("Profit Margin (%)", "Profit Margin (%)", "real")]
        agg = measure_ref("Profit Margin (%)", "AVG")
        val = "AVG([Profit Margin (%)])"
    elif field == "[Sales]" and kpi_name == "KPI - Average Order Value":
        deps = ["<column caption='Sales' datatype='real' name='[Sales]' role='dimension' type='nominal' />",
                "<column caption='Order ID' datatype='string' name='[Order ID]' role='dimension' type='nominal' />"]
        agg = "<column datatype='real' name='SUM([Sales])/COUNTD([Order ID])' role='measure' type='quantitative' />"
        val = "SUM([Sales])/COUNTD([Order ID])"
    else:
        deps = [measure_dependency(field.strip("[]"), field.strip("[]"), dtype)]
        agg = measure_ref(field.strip("[]"), "SUM", dtype)
        val = f"SUM({field})"
    ws.append(worksheet(
        kpi_name,
        ind("\n".join(deps)),
        "",
        ind("    " + agg),
        mark="Text",
    ))

# --- Analysis worksheets ----------------------------------------------------
# 1. Monthly Sales Trend (Month x SUM(Sales), colored by Year)
ws.append(worksheet(
    "Monthly Sales Trend",
    ind("\n".join([
        dependency("[Month]", "Month", "integer", "ordinal"),
        dependency("[Year]", "Year", "integer", "nominal"),
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + dim_ref("[Month]", "integer", "ordinal")),
    ind("        " + measure_ref("Sales", "SUM")),
))

# 2. Monthly Profit Trend
ws.append(worksheet(
    "Monthly Profit Trend",
    ind("\n".join([
        dependency("[Month]", "Month", "integer", "ordinal"),
        dependency("[Year]", "Year", "integer", "nominal"),
        measure_dependency("Profit", "Profit", "real"),
    ])),
    ind("        " + dim_ref("[Month]", "integer", "ordinal")),
    ind("        " + measure_ref("Profit", "SUM")),
))

# 3. Sales by Category
ws.append(worksheet(
    "Sales by Category",
    ind("\n".join([
        dependency("[Category]", "Category", "string", "nominal"),
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + dim_ref("[Category]")),
    ind("        " + measure_ref("Sales", "SUM")),
))

# 4. Profit by Category
ws.append(worksheet(
    "Profit by Category",
    ind("\n".join([
        dependency("[Category]", "Category", "string", "nominal"),
        measure_dependency("Profit", "Profit", "real"),
    ])),
    ind("        " + dim_ref("[Category]")),
    ind("        " + measure_ref("Profit", "SUM")),
))

# 5. Sales by Region
ws.append(worksheet(
    "Sales by Region",
    ind("\n".join([
        dependency("[Region]", "Region", "string", "nominal"),
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + dim_ref("[Region]")),
    ind("        " + measure_ref("Sales", "SUM")),
))

# 6. Top 10 Products by Sales
ws.append(worksheet(
    "Top 10 Products by Sales",
    ind("\n".join([
        dependency("[Product Name]", "Product Name", "string", "nominal"),
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + dim_ref("[Product Name]")),
    ind("        " + measure_ref("Sales", "SUM")),
))

# 7. Bottom 10 Products by Profit
ws.append(worksheet(
    "Bottom 10 Products by Profit",
    ind("\n".join([
        dependency("[Product Name]", "Product Name", "string", "nominal"),
        measure_dependency("Profit", "Profit", "real"),
    ])),
    ind("        " + dim_ref("[Product Name]")),
    ind("        " + measure_ref("Profit", "SUM")),
))

# 8. Sales by Customer Segment
ws.append(worksheet(
    "Sales by Customer Segment",
    ind("\n".join([
        dependency("[Segment]", "Segment", "string", "nominal"),
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + dim_ref("[Segment]")),
    ind("        " + measure_ref("Sales", "SUM")),
))

# 9. Discount vs Profit (scatter)
ws.append(worksheet(
    "Discount vs Profit",
    ind("\n".join([
        dependency("[Category]", "Category", "string", "nominal"),
        measure_dependency("Discount", "Discount", "real"),
        measure_dependency("Profit", "Profit", "real"),
    ])),
    ind("        " + measure_ref("Profit", "SUM")),
    ind("        " + measure_ref("Discount", "AVG")),
    mark="Circle",
))

# 10. Geographic Sales Analysis (State, carries geographic role -> renders as a map)
ws.append(worksheet(
    "Geographic Sales Analysis",
    ind("\n".join([
        "<column caption='State' datatype='string' name='[State]' role='geographic' type='nominal' />",
        measure_dependency("Sales", "Sales", "real"),
    ])),
    ind("        " + "<column datatype='string' name='[State]' role='geographic' type='nominal' />"),
    ind("        " + measure_ref("Sales", "SUM")),
))

# ---------------------------------------------------------------------------
# Dashboard with quick filters
# ---------------------------------------------------------------------------
FILTER_FIELDS = ["Year", "Month", "Category", "Sub-Category", "Region", "Segment",
                 "Customer Name", "Product Name"]

dashboard = f"""  <dashboard name='E-Commerce Analytics Dashboard' style-version='2'>
    <style>
      <class value='tab' />
      <floating-zone value='false' />
    </style>
    <zones>
      <zone h='1400' w='2000' x='0' y='0'>
        <zone h='120' w='2000' x='0' y='0'>
          <zone h='120' w='250' x='0' y='0' name='KPI - Total Sales' style-version='2' type='worksheet' />
          <zone h='120' w='250' x='250' y='0' name='KPI - Total Profit' style-version='2' type='worksheet' />
          <zone h='120' w='250' x='500' y='0' name='KPI - Total Orders' style-version='2' type='worksheet' />
          <zone h='120' w='250' x='750' y='0' name='KPI - Total Quantity' style-version='2' type='worksheet' />
          <zone h='120' w='250' x='1000' y='0' name='KPI - Average Order Value' style-version='2' type='worksheet' />
          <zone h='120' w='250' x='1250' y='0' name='KPI - Profit Margin' style-version='2' type='worksheet' />
        </zone>
        <zone h='1280' w='2000' x='0' y='120'>
          <zone h='300' w='700' x='0' y='0' name='Monthly Sales Trend' style-version='2' type='worksheet' />
          <zone h='300' w='700' x='700' y='0' name='Monthly Profit Trend' style-version='2' type='worksheet' />
          <zone h='300' w='600' x='1400' y='0' name='Sales by Category' style-version='2' type='worksheet' />
          <zone h='300' w='600' x='0' y='300' name='Profit by Category' style-version='2' type='worksheet' />
          <zone h='300' w='600' x='600' y='300' name='Sales by Region' style-version='2' type='worksheet' />
          <zone h='300' w='600' x='1200' y='300' name='Sales by Customer Segment' style-version='2' type='worksheet' />
          <zone h='300' w='700' x='0' y='600' name='Top 10 Products by Sales' style-version='2' type='worksheet' />
          <zone h='300' w='700' x='700' y='600' name='Bottom 10 Products by Profit' style-version='2' type='worksheet' />
          <zone h='300' w='600' x='1400' y='600' name='Discount vs Profit' style-version='2' type='worksheet' />
          <zone h='380' w='2000' x='0' y='900' name='Geographic Sales Analysis' style-version='2' type='worksheet' />
        </zone>
      </zone>
    </zones>
    <quickfilters>
"""

for i, f in enumerate(FILTER_FIELDS):
    dashboard += (
        f"      <quickfilter name='{f}' worksheet='Monthly Sales Trend' style-version='2' "
        f"zone-id='qf-{i}'>\n"
        f"        <zone id='qf-{i}' name='{f}' style-version='2' type='quickfilter' />\n"
        f"      </quickfilter>\n"
    )

dashboard += """    </quickfilters>
  </dashboard>
"""

# ---------------------------------------------------------------------------
# Datasource columns
# ---------------------------------------------------------------------------
ds_columns = []
for col_name, caption, datatype, type_, geo in DIM_COLS:
    geo_attr = f" role='geographic'" if geo else ""
    ds_columns.append(
        f"        <column caption='{caption}' datatype='{datatype}' name='{col_name}'{geo_attr} "
        f"type='{type_}' />"
    )
for col_name, caption, datatype, type_ in MEASURE_COLS:
    ds_columns.append(
        f"        <column caption='{caption}' datatype='{datatype}' name='{col_name}' "
        f"type='{type_}' />"
    )

dbname = str(CSV_PATH).replace("\\", "\\\\")
filename = "ecommerce_clean.csv"

workbook = f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook source-build='2022.3.0' source-platform='win' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <preferences>
    <preference name='default-highlighting-color' value='#d5e5f2' />
    <preference name='ui.encoding.shelf.height' value='32' />
    <preference name='ui.shelf.height' value='27' />
  </preferences>
  <datasources>
    <datasource caption='ecommerce_clean' inline='true' name='ecommerce_clean' version='18.1'>
      <connection class='federated'>
        <named-connections>
          <named-connection caption='ecommerce_clean.csv' name='ecommerce_clean.csv'>
            <connection authentication='none' class='csv' dbname='{dbname}' filename='{filename}' />
          </named-connection>
        </named-connections>
        <relation connection='ecommerce_clean.csv' name='ecommerce_clean' table='ecommerce_clean' type='table' />
        <aliases enabled='yes' />
{chr(10).join(ds_columns)}
        <layout-cols class='col0' />
        <layout-rows class='row0' />
      </connection>
{chr(10).join(ds_columns)}
    </datasource>
  </datasources>
  <worksheets>
{chr(10).join(ws)}
  </worksheets>
{dashboard}
  <windows>
    <window class='caption-window' name='dashboard' />
    <window class='dashboard' name='E-Commerce Analytics Dashboard' />
  </windows>
</workbook>
"""

TWB_PATH.parent.mkdir(parents=True, exist_ok=True)
TWB_PATH.write_text(workbook, encoding="utf-8")
print(f"Workbook written to {TWB_PATH.name} ({TWB_PATH.stat().st_size:,} bytes)")
print(f"Connected to: {CSV_PATH.name} in the {CSV_PATH.parent.name} folder")
