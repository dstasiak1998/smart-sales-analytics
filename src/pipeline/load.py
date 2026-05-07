import pandas as pd
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Boolean, DateTime
from datetime import datetime
from loguru import logger
from src.utils.config import settings


class Base(DeclarativeBase):
    pass


class Sale(Base):
    __tablename__ = "sales"

    id:          Mapped[int]      = mapped_column(
                                       Integer,
                                       primary_key=True,
                                       autoincrement=True,
                                   )
    order_id:    Mapped[str]      = mapped_column(
                                       String(36),
                                       unique=True,
                                       nullable=False,
                                   )
    customer:    Mapped[str]      = mapped_column(String(200))
    email:       Mapped[str]      = mapped_column(String(200))
    product:     Mapped[str]      = mapped_column(String(100))
    category:    Mapped[str]      = mapped_column(String(50))
    region:      Mapped[str]      = mapped_column(String(20))
    quantity:    Mapped[int]      = mapped_column(Integer)
    unit_price:  Mapped[float]    = mapped_column(Float)
    total:       Mapped[float]    = mapped_column(Float)
    revenue:     Mapped[float]    = mapped_column(Float)
    order_date:  Mapped[datetime] = mapped_column(DateTime)
    is_returned: Mapped[bool]     = mapped_column(Boolean)
    year:        Mapped[int]      = mapped_column(Integer)
    month:       Mapped[int]      = mapped_column(Integer)
    quarter:     Mapped[int]      = mapped_column(Integer)


def get_engine() -> Engine:
    """Tworzy i zwraca połączenie z bazą danych."""
    engine = create_engine(
        settings.db_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    logger.info(
        f"Połączono z bazą: "
        f"{settings.db_host}:{settings.db_port}"
        f"/{settings.db_name}"
    )
    return engine


def init_db(engine: Engine) -> None:
    """Tworzy tabele w bazie danych jeśli nie istnieją."""
    Base.metadata.create_all(engine)
    logger.info("Schemat bazy danych gotowy")


def test_connection(engine: Engine) -> bool:
    """Sprawdza czy połączenie z bazą działa."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.success("Połączenie z bazą danych działa poprawnie")
        return True
    except Exception as e:
        logger.error(f"Błąd połączenia z bazą: {e}")
        return False


def load(
    df: pd.DataFrame,
    engine: Engine,
    mode: str = "append",
) -> None:
    """Zapisuje DataFrame do tabeli sales w bazie danych."""
    columns_to_load = [
        "order_id", "customer", "email", "product",
        "category", "region", "quantity", "unit_price",
        "total", "revenue", "order_date", "is_returned",
        "year", "month", "quarter",
    ]

    df_to_load = df[columns_to_load].copy()

    df_to_load.to_sql(
        name="sales",
        con=engine,
        if_exists=mode,
        index=False,
        method="multi",
        chunksize=500,
    )

    logger.success(
        f"Załadowano {len(df_to_load)} rekordów "
        f"do tabeli 'sales' (tryb: {mode})"
    )


def get_row_count(engine: Engine) -> int:
    """Zwraca aktualną liczbę rekordów w tabeli sales."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM sales"))
        count = result.scalar()
    logger.info(f"Tabela 'sales' zawiera {count} rekordów")
    return count