"""Persistence operations for cars; no UI or demo-data generation."""
from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert

from db import cars


class RepositoryError(Exception):
    """A car persistence operation failed."""


class InvalidCarError(RepositoryError):
    """A car violates a database constraint, including duplicate identity."""


class CarRepository:
    def __init__(self, engine: Engine):
        self._engine = engine

    def list_all(self) -> pd.DataFrame:
        """Return all cars in stable ID order, including columns when empty."""
        try:
            with self._engine.connect() as connection:
                return pd.read_sql(select(cars).order_by(cars.c.id), connection)
        except SQLAlchemyError as error:
            raise RepositoryError("Could not read cars.") from error

    def add(self, values: Mapping[str, Any]) -> None:
        self._execute_write(cars.insert().values(**values))

    def add_missing(self, values: Iterable[Mapping[str, Any]]) -> None:
        """Insert a batch atomically, skipping existing car identities."""
        rows = list(values)
        if not rows:
            return
        statement = insert(cars).values(rows).on_conflict_do_nothing(
            constraint="car_identity"
        )
        self._execute_write(statement)

    def _execute_write(self, statement) -> None:
        try:
            with self._engine.begin() as connection:
                connection.execute(statement)
        except IntegrityError as error:
            raise InvalidCarError("Car data violates a database constraint.") from error
        except SQLAlchemyError as error:
            raise RepositoryError("Could not save cars.") from error
