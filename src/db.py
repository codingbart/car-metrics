from functools import lru_cache
from pathlib import Path

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    create_engine
)
from sqlalchemy.engine import Engine

from attributes import ATTRIBUTES

DATABASE_PATH = Path(__file__).parent.parent / "cars.db"
IDENTITY_COLUMNS = ("brand", "model", "variant", "year")


def _build_value_constraint() -> str:
    conditions = [
        f"{attribute.key} {'>=' if attribute.allows_zero else '>'} 0"
        for attribute in ATTRIBUTES
    ]

    return " AND ".join(conditions)


metadata = MetaData()
cars = Table(
    "cars",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("brand", String(80), nullable=False),
    Column("model", String(100), nullable=False),
    Column("variant", String(100), nullable=False),
    Column("year", Integer, nullable=False),
    *(Column(attribute.key, Float, nullable=False) for attribute in ATTRIBUTES),
    Column("source_url", String(1000), nullable=False),
    Column("source_date", Date, nullable=False),
    CheckConstraint(_build_value_constraint()),
    CheckConstraint("year BETWEEN 1900 AND 2100"),
    UniqueConstraint(*IDENTITY_COLUMNS, name="car_identity")
)


@lru_cache
def get_engine() -> Engine:
    return create_engine(f"sqlite:///{DATABASE_PATH}")


def create_schema(engine: Engine) -> None:
    metadata.create_all(engine)
