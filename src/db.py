import os
from functools import lru_cache

from sqlalchemy import (Boolean, CheckConstraint, Column, Date, Float, Integer,
                        MetaData, String, Table, UniqueConstraint, create_engine)
from sqlalchemy.engine import URL

metadata = MetaData()
cars = Table(
    "cars", metadata,
    Column("id", Integer, primary_key=True),
    Column("brand", String(80), nullable=False),
    Column("model", String(100), nullable=False),
    Column("variant", String(100), nullable=False),
    Column("year", Integer, nullable=False),
    Column("power", Float, nullable=False),
    Column("fuel", Float, nullable=False),
    Column("trunk", Float, nullable=False),
    Column("price", Float, nullable=False),
    Column("speed", Float, nullable=False),
    Column("source_url", String(1000), nullable=False),
    Column("source_date", Date, nullable=False),
    Column("is_demo", Boolean, nullable=False, default=False),
    CheckConstraint("power > 0 AND fuel > 0 AND trunk >= 0 AND price > 0 AND speed > 0"),
    CheckConstraint("year BETWEEN 1900 AND 2100"),
    UniqueConstraint("brand", "model", "variant", "year", name="car_identity"),
)


@lru_cache
def engine():
    url = os.getenv("DATABASE_URL") or URL.create(
        "postgresql+psycopg", username="autometry",
        password=os.getenv("DB_PASSWORD", "autometry_local"),
        host=os.getenv("DB_HOST", "localhost"), database="autometry")
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})


def initialize(db_engine):
    """Create the schema using the same engine as the repository."""
    metadata.create_all(db_engine)
