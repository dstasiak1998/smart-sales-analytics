from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Literal
import pandas as pd
from loguru import logger


VALID_CATEGORIES = Literal[
    "Electronics", "Clothing", "Food", "Books"
]
VALID_REGIONS = Literal[
    "NORTH", "SOUTH", "EAST", "WEST"
]
VALID_PRICE_TIERS = Literal[
    "budget", "mid", "premium", "luxury"
]


class SaleRecord(BaseModel):
    order_id:    str
    customer:    str
    email:       EmailStr
    product:     str
    category:    VALID_CATEGORIES
    region:      VALID_REGIONS
    quantity:    int
    unit_price:  float
    total:       float
    order_date:  datetime
    is_returned: bool

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError(
                f"quantity musi być większe od 0, otrzymano: {v}"
            )
        return v

    @field_validator("unit_price", "total")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError(
                f"cena nie może być ujemna, otrzymano: {v}"
            )
        return v

    @field_validator("customer")
    @classmethod
    def customer_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("nazwa klienta nie może być pusta")
        return v


class ValidationReport:
    def __init__(self) -> None:
        self.valid_count:   int       = 0
        self.invalid_count: int       = 0
        self.errors:        list[dict] = []

    def add_error(
        self,
        order_id: str,
        error: str,
    ) -> None:
        self.invalid_count += 1
        self.errors.append({
            "order_id": order_id,
            "error":    error,
        })

    def add_valid(self) -> None:
        self.valid_count += 1

    def summary(self) -> str:
        total = self.valid_count + self.invalid_count
        return (
            f"Walidacja: {self.valid_count}/{total} rekordów OK, "
            f"{self.invalid_count} odrzuconych"
        )


def validate_df(df: pd.DataFrame) -> pd.DataFrame:
    """Waliduje każdy wiersz — zwraca tylko poprawne rekordy."""
    valid_rows = []
    report     = ValidationReport()

    for row in df.to_dict("records"):
        order_id = str(row.get("order_id", "UNKNOWN"))
        try:
            SaleRecord(**row)
            valid_rows.append(row)
            report.add_valid()
        except Exception as e:
            report.add_error(order_id, str(e))

    if report.invalid_count > 0:
        logger.warning(f"Odrzucone rekordy: {report.invalid_count}")
        for err in report.errors[:5]:
            logger.warning(
                f"  order_id={err['order_id']} → {err['error']}"
            )
        if report.invalid_count > 5:
            logger.warning(
                f"  ... i {report.invalid_count - 5} więcej"
            )

    logger.success(report.summary())
    return pd.DataFrame(valid_rows)