import pandas as pd
import streamlit as st

from cars import DISPLAY_NAME
from ui.formatting import format_number
from ui.inputs import select_attribute

ICON = ":primary[:material/directions_car:]"
MAX_ICONS = 200
MAX_COMPARED_CARS = 6
CARS_COMPARED_BY_DEFAULT = 4


def count_icons(*, value: float, pictogram_unit: float) -> int:
    return min(round(value / pictogram_unit), MAX_ICONS)


def build_pictogram_row(*, name: str, value_text: str, icon_count: int) -> str:
    return f"**{name}**: `{value_text}`  \n{ICON * icon_count}"


def render_pictogram(cars: pd.DataFrame) -> None:
    st.subheader("Garaż obrazkowy")

    attribute = select_attribute("Co porównujesz?")
    names: list[str] = cars[DISPLAY_NAME].tolist()
    selected_names = st.multiselect(
        f"Wybierz do {MAX_COMPARED_CARS} samochodów",
        names,
        default=names[:CARS_COMPARED_BY_DEFAULT],
        max_selections=MAX_COMPARED_CARS
    )

    pictogram_unit = format_number(attribute.pictogram_unit, decimals=0)
    st.markdown(f"{ICON} = {pictogram_unit} {attribute.unit}")

    for _, car in cars[cars[DISPLAY_NAME].isin(selected_names)].iterrows():
        value = car[attribute.key]
        icon_count = count_icons(value=value, pictogram_unit=attribute.pictogram_unit)
        row = build_pictogram_row(
            name=car[DISPLAY_NAME],
            value_text=format_number(value, attribute.decimals),
            icon_count=icon_count
        )

        st.markdown(row)
