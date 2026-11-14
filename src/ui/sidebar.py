import pandas as pd
import streamlit as st

from attributes import PRICE
from dataset import QAR_TO_PLN, SOURCE_URL
from ui.formatting import format_number

BUDGET_STEP = 10000.0


def render_data_panel() -> None:
    exchange_rate = format_number(QAR_TO_PLN, decimals=4)

    with st.sidebar:
        st.header("Baza samochodów")
        st.caption(f"Zbiór [Qatar Cars]({SOURCE_URL}) (P. Musgrave, 2025, CC BY 4.0).")
        st.caption(
            "Bez aut elektrycznych; ceny przeliczone z riali katarskich "
            f"po kursie NBP `{exchange_rate}`."
        )


def render_filters(cars: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        st.header("Filtry")

        brands = st.multiselect("Marki", sorted(cars.brand.unique()))
        selection = cars[cars.brand.isin(brands)] if brands else cars

        budget = st.number_input(
            f"Maksymalna cena [{PRICE.unit}]",
            min_value=0.0,
            value=float(selection[PRICE.key].max()),
            step=BUDGET_STEP
        )

    return selection[selection[PRICE.key] <= budget].copy()
