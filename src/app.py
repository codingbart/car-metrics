from typing import NoReturn

import pandas as pd
import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

import db
from cars import add_display_name
from dataset import import_qatar_cars
from repository import CarRepository, RepositoryError
from ui.header import render_page_header
from ui.sidebar import render_data_panel, render_filters
from ui.tabs import render_tabs

REQUIRED_CARS = 30


def stop_with_database_error() -> NoReturn:
    st.error(f"Nie można otworzyć bazy danych SQLite: {db.DATABASE_PATH}")
    st.stop()


def connect_or_stop() -> CarRepository:
    try:
        engine = db.get_engine()
        db.create_schema(engine)
    except SQLAlchemyError:
        stop_with_database_error()

    return CarRepository(engine)


def read_or_import_cars(repository: CarRepository) -> pd.DataFrame:
    cars = repository.list_all()

    if cars.empty:
        import_qatar_cars(repository)
        cars = repository.list_all()

    return cars


def read_cars_or_stop(repository: CarRepository) -> pd.DataFrame:
    try:
        return read_or_import_cars(repository)
    except RepositoryError:
        stop_with_database_error()


def main() -> None:
    st.set_page_config(page_title="Statystyka w informatyce", layout="wide")
    render_page_header()

    repository = connect_or_stop()
    cars = read_cars_or_stop(repository)

    render_data_panel()
    selection = render_filters(cars)

    if selection.empty:
        st.info("Brak samochodów dla wybranych filtrów. Zmień filtry.")
        st.stop()

    if len(selection) < REQUIRED_CARS:
        st.info(
            f"Analizujesz {len(selection)} obiektów. "
            f"Projekt wymaga co najmniej {REQUIRED_CARS} obiektów w zbiorze docelowym."
        )

    selection = add_display_name(selection)
    render_tabs(selection)


main()
