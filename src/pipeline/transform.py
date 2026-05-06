import pandas as pd
from loguru import logger


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Usuwa duplikaty i wiersze z brakującymi kluczowymi danymi."""
    before = len(df)

    df = df.drop_duplicates(subset=["order_id"])

    df = df.dropna(subset=["order_id", "email", "total"])

    df = df[df["quantity"] > 0]
    df = df[df["unit_price"] > 0]
    df = df[df["total"] > 0]

    removed = before - len(df)
    logger.info(f"Czyszczenie: usunięto {removed} błędnych wierszy")
    logger.info(f"Pozostało {len(df)} rekordów po czyszczeniu")

    return df


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Ujednolica formaty tekstowe i typy danych."""
    df = df.copy()

    df["email"]    = df["email"].str.lower().str.strip()
    df["customer"] = df["customer"].str.strip()
    df["product"]  = df["product"].str.strip().str.title()
    df["category"] = df["category"].str.strip().str.title()
    df["region"]   = df["region"].str.strip().str.upper()

    df["total"]      = df["total"].clip(lower=0)
    df["unit_price"] = df["unit_price"].clip(lower=0)

    df["order_date"] = pd.to_datetime(df["order_date"])

    logger.info("Normalizacja: ujednolicono formaty danych")

    return df


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Dodaje nowe kolumny przydatne w analizie biznesowej."""
    df = df.copy()

    df["year"]    = df["order_date"].dt.year
    df["month"]   = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["weekday"] = df["order_date"].dt.day_name()
    df["week"]    = df["order_date"].dt.isocalendar().week.astype(int)

    df["revenue"] = df.apply(
        lambda row: 0.0 if row["is_returned"] else row["total"],
        axis=1,
    )

    df["price_tier"] = pd.cut(
        df["unit_price"],
        bins=[0, 50, 150, 300, float("inf")],
        labels=["budget", "mid", "premium", "luxury"],
    )

    logger.info(f"Wzbogacanie: dodano 7 nowych kolumn analitycznych")

    return df


def save_processed(
    df: pd.DataFrame,
    path: str = "data/processed/sales_clean.csv",
) -> None:
    """Zapisuje przetworzone dane do pliku CSV."""
    from pathlib import Path
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info(f"Zapisano przetworzone dane do {path}")


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Główna funkcja łącząca wszystkie kroki transformacji."""
    logger.info("=== START TRANSFORM ===")

    df = clean(df)
    df = normalize(df)
    df = enrich(df)

    logger.success(
        f"=== TRANSFORM ZAKOŃCZONY: {len(df)} rekordów ==="
    )

    return df