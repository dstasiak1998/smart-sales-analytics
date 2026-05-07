from faker import Faker
from datetime import datetime, timedelta
import pandas as pd
import random
from pathlib import Path


fake = Faker("pl_PL")

CATEGORIES = ["Electronics", "Clothing", "Food", "Books"]
REGIONS = ["North", "South", "East", "West"]
PRODUCTS = {
    "Electronics": ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"],
    "Clothing":    ["Jacket", "Shirt", "Trousers", "Shoes", "Hat"],
    "Food":        ["Coffee", "Tea", "Chocolate", "Honey", "Oil"],
    "Books":       ["Novel", "Guide", "Textbook", "Comic", "Atlas"],
}


def generate_sales(n_records: int = 1000) -> pd.DataFrame:
    """Generuje n_records wierszy fikcyjnych danych sprzedażowych."""
    records = []
    start = datetime(2024, 1, 1)

    for _ in range(n_records):
        category = random.choice(CATEGORIES)
        product  = random.choice(PRODUCTS[category])
        qty      = random.randint(1, 20)
        price    = round(random.uniform(9.99, 499.99), 2)

        records.append({
            "order_id"   : fake.uuid4(),
            "customer"   : fake.name(),
            "email"      : fake.email(),
            "product"    : product,
            "category"   : category,
            "region"     : random.choice(REGIONS),
            "quantity"   : qty,
            "unit_price" : price,
            "total"      : round(qty * price, 2),
            "order_date" : start + timedelta(
                               days=random.randint(0, 364)
                           ),
            "is_returned": random.random() < 0.05,
        })

    return pd.DataFrame(records)


def save_raw(
    df: pd.DataFrame,
    path: str = "data/raw/sales.csv",
) -> None:
    """Zapisuje surowe dane do pliku CSV."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Zapisano {len(df)} rekordów do {path}")


def load_raw(
    path: str = "data/raw/sales.csv",
) -> pd.DataFrame:
    """Wczytuje surowe dane z pliku CSV."""
    if not Path(path).exists():
        raise FileNotFoundError(
            f"Plik {path} nie istnieje. "
            f"Uruchom najpierw generate_sales()."
        )
    return pd.read_csv(path, parse_dates=["order_date"])