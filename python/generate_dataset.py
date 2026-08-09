"""
generate_dataset.py
===================
Generates a synthetic e-commerce sales dataset (5,000+ transaction records).

This dataset is FULLY SYNTHETIC and was created programmatically to mimic the
structure and behaviour of a real e-commerce order book (similar in shape to a
classic "Superstore" sales table). All customer names, addresses and values are
fabricated. No real customer or business data is included.

The script uses a fixed random seed so the generated dataset is fully
reproducible.

Output : data/ecommerce_dataset.csv
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SEED = 42
N_ORDERS = 5_500  # number of order-line transaction records (> 5,000)

DATE_START = date(2019, 1, 1)
DATE_END = date(2023, 12, 31)

# Paths are resolved relative to the project root so the script can be run
# from anywhere inside the repository.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "ecommerce_dataset.csv"

# ---------------------------------------------------------------------------
# Product catalogue
# ---------------------------------------------------------------------------
# sub_category -> (average unit price, price spread)
CATALOGUE = {
    "Technology": {
        "Phones": (350.0, 250.0),
        "Machines": (420.0, 260.0),
        "Accessories": (75.0, 60.0),
        "Copiers": (850.0, 350.0),
    },
    "Furniture": {
        "Chairs": (340.0, 220.0),
        "Tables": (460.0, 300.0),
        "Bookcases": (190.0, 120.0),
        "Furnishings": (55.0, 45.0),
    },
    "Office Supplies": {
        "Binders": (45.0, 35.0),
        "Paper": (38.0, 25.0),
        "Storage": (95.0, 70.0),
        "Appliances": (300.0, 180.0),
        "Labels": (18.0, 12.0),
        "Art": (75.0, 55.0),
        "Envelopes": (22.0, 15.0),
        "Fasteners": (14.0, 10.0),
        "Supplies": (28.0, 18.0),
    },
}

PRODUCT_PREFIX = {"Technology": "TEC", "Furniture": "FUR", "Office Supplies": "OFF"}

# Profit model: (base margin, discount sensitivity)
PROFIT_MODEL = {
    "Technology": (0.24, 0.55),
    "Furniture": (0.16, 0.62),
    "Office Supplies": (0.20, 0.30),
}

# ---------------------------------------------------------------------------
# Geography (Country = United States)
# ---------------------------------------------------------------------------
STATES_BY_REGION = {
    "West": ["California", "Washington", "Oregon", "Nevada", "Arizona", "Colorado", "Utah"],
    "East": ["New York", "Massachusetts", "Pennsylvania", "New Jersey", "Maryland", "Virginia", "Connecticut"],
    "Central": ["Texas", "Illinois", "Missouri", "Kansas", "Oklahoma", "Minnesota", "Wisconsin"],
    "South": ["Florida", "Georgia", "North Carolina", "Tennessee", "Alabama", "Louisiana", "Kentucky"],
}

CITIES_BY_STATE = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "Fresno"],
    "Washington": ["Seattle", "Spokane", "Tacoma", "Bellevue"],
    "Oregon": ["Portland", "Salem", "Eugene"],
    "Nevada": ["Las Vegas", "Reno", "Henderson"],
    "Arizona": ["Phoenix", "Tucson", "Mesa", "Scottsdale"],
    "Colorado": ["Denver", "Boulder", "Colorado Springs", "Aurora"],
    "Utah": ["Salt Lake City", "Provo", "Ogden"],
    "New York": ["New York City", "Buffalo", "Rochester", "Albany"],
    "Massachusetts": ["Boston", "Worcester", "Springfield", "Cambridge"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Harrisburg", "Allentown"],
    "New Jersey": ["Newark", "Jersey City", "Trenton", "Paterson"],
    "Maryland": ["Baltimore", "Annapolis", "Silver Spring"],
    "Virginia": ["Virginia Beach", "Richmond", "Norfolk", "Arlington"],
    "Connecticut": ["Hartford", "New Haven", "Stamford"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
    "Illinois": ["Chicago", "Springfield", "Peoria", "Naperville"],
    "Missouri": ["Kansas City", "St. Louis", "Springfield"],
    "Kansas": ["Wichita", "Overland Park", "Topeka"],
    "Oklahoma": ["Oklahoma City", "Tulsa", "Norman"],
    "Minnesota": ["Minneapolis", "St. Paul", "Rochester", "Duluth"],
    "Wisconsin": ["Milwaukee", "Madison", "Green Bay"],
    "Iowa": ["Des Moines", "Cedar Rapids", "Davenport"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Fort Lauderdale"],
    "Georgia": ["Atlanta", "Savannah", "Augusta", "Athens"],
    "North Carolina": ["Charlotte", "Raleigh", "Durham", "Greensboro"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
    "Alabama": ["Birmingham", "Montgomery", "Mobile"],
    "Louisiana": ["New Orleans", "Baton Rouge", "Shreveport"],
    "Kentucky": ["Louisville", "Lexington", "Frankfort"],
}

SHIPPING_MODES = [
    ("Standard Class", 5.0, 0.10),
    ("Second Class", 8.0, 0.12),
    ("First Class", 12.0, 0.15),
    ("Same Day", 20.0, 0.18),
]

PAYMENT_MODES = ["Credit Card", "Debit Card", "Cash on Delivery", "UPI", "Net Banking"]

# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph",
    "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Nancy", "Matthew",
    "Lisa", "Anthony", "Betty", "Donald", "Sandra", "Mark", "Ashley", "Paul",
    "Kimberly", "Steven", "Emily", "Andrew", "Donna", "Kenneth", "Michelle",
    "Joshua", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason",
    "Sharon", "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen",
    "Gary", "Amy", "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Emma",
    "Stephen", "Brenda", "Larry", "Pamela", "Justin", "Maria", "Scott", "Nicole",
    "Brandon", "Anna", "Benjamin", "Olivia", "Samuel", "Katherine", "Gregory",
    "Samantha", "Alexander", "Christine", "Patrick", "Sophia", "Frank", "Isabella",
    "Raymond", "Victoria", "Jack", "Mia", "Dennis", "Harper", "Jerry", "Evelyn",
    "Tyler", "Chloe", "Aaron", "Ella", "Jose", "Grace", "Adam", "Hannah",
    "Henry", "Nora", "Rahul", "Priya", "Arjun", "Sneha", "Vikram", "Ananya",
    "Ravi", "Divya", "Kiran", "Meera", "Deepak", "Pooja", "Anil", "Kavya",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner",
    "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
    "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
    "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox",
    "Ward", "Richardson", "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett",
    "Gray", "Mendoza", "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders",
    "Patel", "Kumar", "Sharma", "Gupta", "Reddy", "Nair", "Das", "Singh",
]

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.50, 0.32, 0.18]


def build_customers(rng: np.random.Generator, n: int = 650) -> pd.DataFrame:
    """Create a pool of synthetic customers."""
    first = rng.choice(FIRST_NAMES, size=n)
    last = rng.choice(LAST_NAMES, size=n)
    customers = []
    used = set()
    for i in range(n):
        name = f"{first[i]} {last[i]}"
        # Keep names unique for clean customer identification
        while name in used:
            last[i] = rng.choice(LAST_NAMES)
            name = f"{first[i]} {last[i]}"
        used.add(name)
        segment = rng.choice(SEGMENTS, p=SEGMENT_WEIGHTS)
        cid = f"CUS-{i + 1:04d}"
        customers.append({"Customer ID": cid, "Customer Name": name, "Segment": segment})
    return pd.DataFrame(customers)


def build_products(rng: np.random.Generator) -> pd.DataFrame:
    """Create the product catalogue with one row per product."""
    products = []
    counter = 1
    for category, subcats in CATALOGUE.items():
        for subcat, (base, spread) in subcats.items():
            # Between 6 and 10 products per sub-category
            n_products = int(rng.integers(6, 10))
            for _ in range(n_products):
                pid = f"{PRODUCT_PREFIX[category]}-{counter:04d}"
                counter += 1
                # Realistic product names built from descriptive words
                brand = rng.choice(
                    ["Nova", "TechPro", "Ergo", "Prime", "Vertex", "Apex", "Summit",
                     "Titan", "Luma", "Orbit", "Zenith", "Pioneer"]
                )
                products.append({
                    "Product ID": pid,
                    "Product Name": f"{brand} {subcat} {rng.integers(100, 999)}",
                    "Category": category,
                    "Sub-Category": subcat,
                    "Base Price": round(base * rng.uniform(0.85, 1.15) * (1 + spread / base * 0.5), 2),
                })
    return pd.DataFrame(products)


def weighted_date(rng: np.random.Generator) -> date:
    """Pick a date with realistic seasonality (Nov/Dec peaks, Jan/Feb dips)."""
    year = rng.integers(DATE_START.year, DATE_END.year + 1)
    month_weight = [0.065, 0.062, 0.075, 0.080, 0.085, 0.080, 0.085, 0.085, 0.088, 0.090, 0.105, 0.100]
    month = rng.choice(range(1, 13), p=month_weight)
    day = rng.integers(1, 29)
    d = date(year, month, day)
    if d > DATE_END:
        d = DATE_END
    return d


def main() -> None:
    rng = np.random.default_rng(SEED)
    random.seed(SEED)

    customers_df = build_customers(rng)
    products_df = build_products(rng)

    rows = []
    order_counter = 1

    for _ in range(N_ORDERS):
        order_date = weighted_date(rng)

        cust = customers_df.iloc[int(rng.integers(0, len(customers_df)))]
        prod = products_df.iloc[int(rng.integers(0, len(products_df)))]

        region = rng.choice(list(STATES_BY_REGION.keys()))
        state = rng.choice(STATES_BY_REGION[region])
        city = rng.choice(CITIES_BY_STATE[state])

        quantity = int(rng.choice([1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5, 6, 7]))

        # Discount levels matching a real-world order book
        discount = rng.choice([0.0, 0.0, 0.0, 0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5])

        unit_price = prod["Base Price"] * rng.uniform(0.9, 1.2) * (1 - discount)
        sales = round(unit_price * quantity, 2)

        # Profit model with discount penalty (high discounts squeeze profit)
        base_margin, sensitivity = PROFIT_MODEL[prod["Category"]]
        margin = base_margin - sensitivity * discount + rng.normal(0.0, 0.05)
        profit = round(sales * margin, 2)

        shipping_mode, base_cost, rate = SHIPPING_MODES[int(rng.integers(0, len(SHIPPING_MODES)))]
        shipping_cost = round(base_cost + rate * sales * rng.uniform(0.05, 0.3), 2)

        payment_mode = rng.choice(PAYMENT_MODES)

        order_id = f"CA-{order_date.year}-{10000 + order_counter:05d}"
        order_counter += 1

        rows.append({
            "Order ID": order_id,
            "Order Date": order_date.isoformat(),
            "Customer ID": cust["Customer ID"],
            "Customer Name": cust["Customer Name"],
            "Segment": cust["Segment"],
            "Country": "United States",
            "State": state,
            "City": city,
            "Region": region,
            "Product ID": prod["Product ID"],
            "Product Name": prod["Product Name"],
            "Category": prod["Category"],
            "Sub-Category": prod["Sub-Category"],
            "Sales": sales,
            "Quantity": quantity,
            "Discount": discount,
            "Profit": profit,
            "Shipping Cost": shipping_cost,
            "Shipping Mode": shipping_mode,
            "Payment Mode": payment_mode,
        })

    df = pd.DataFrame(rows)

    # Shuffle rows so the file does not appear artificially ordered
    df = df.sample(frac=1.0, random_state=SEED).reset_index(drop=True)

    # Introduce a small amount of realistic data-quality noise so the cleaning
    # stage has genuine work to do (missing values + duplicate rows)
    rng2 = np.random.default_rng(SEED + 1)

    # ~0.5% of shipping-cost values missing (simulates unrecorded shipment fees)
    miss_idx = rng2.choice(df.index, size=int(len(df) * 0.005), replace=False)
    df.loc[miss_idx, "Shipping Cost"] = np.nan

    # A handful of fully-duplicated rows (simulates double-entered orders)
    dup_idx = rng2.choice(df.index, size=8, replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Generated {len(df):,} transaction records.")
    print(f"Saved to {OUTPUT_PATH.name} inside the {OUTPUT_PATH.parent.name} folder.")
    print(f"Date range: {df['Order Date'].min()} to {df['Order Date'].max()}")
    print(f"Categories: {df['Category'].nunique()} | "
          f"Products: {df['Product ID'].nunique()} | "
          f"Customers: {df['Customer ID'].nunique()}")


if __name__ == "__main__":
    main()
