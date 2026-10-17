import os
from datetime import date
from functools import lru_cache

import pandas as pd
from sqlalchemy import (Boolean, CheckConstraint, Column, Date, Float, Integer,
                        MetaData, String, Table, UniqueConstraint, create_engine, select)
from sqlalchemy.engine import URL
from sqlalchemy.dialects.postgresql import insert

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


def initialize():
    metadata.create_all(engine())


def read_cars():
    with engine().connect() as conn:
        return pd.read_sql(select(cars).order_by(cars.c.id), conn)


def add_car(values):
    with engine().begin() as conn:
        conn.execute(cars.insert().values(**values))


def seed_demo():
    # Fictional objects: deterministic examples, never manufacturer specifications.
    rows = []
    for i in range(30):
        rows.append(dict(
            brand=["Demo City", "Demo Touring", "Demo Sport"][i % 3],
            model=f"Model {i + 1:02d}", variant="Benzyna — symulacja", year=2024,
            power=75 + i * 7, fuel=round(4.5 + i * .10 + (i % 4) * .3, 1),
            trunk=240 + (i * 37) % 400, price=65000 + i * 5600 + (i % 3) * 7000,
            speed=155 + i * 3, source_url="Dane syntetyczne — generator db.py",
            source_date=date(2026, 10, 14), is_demo=True))
    with engine().begin() as conn:
        conn.execute(insert(cars).values(rows).on_conflict_do_nothing(constraint="car_identity"))
