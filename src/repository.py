from collections.abc import Iterable, Mapping
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.sqlite import insert

from db import IDENTITY_COLUMNS, cars


class RepositoryError(Exception):
    pass


class CarRepository:
    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def list_all(self) -> pd.DataFrame:
        try:
            with self._engine.connect() as connection:
                return pd.read_sql(select(cars).order_by(cars.c.id), connection)
        except SQLAlchemyError as error:
            raise RepositoryError("Could not read cars.") from error

    def add_missing(self, values: Iterable[Mapping[str, Any]]) -> None:
        rows = list(values)
        if not rows:
            return

        statement = insert(cars).values(rows).on_conflict_do_nothing(
            index_elements=IDENTITY_COLUMNS
        )

        try:
            with self._engine.begin() as connection:
                connection.execute(statement)
        except SQLAlchemyError as error:
            raise RepositoryError("Could not save cars.") from error
