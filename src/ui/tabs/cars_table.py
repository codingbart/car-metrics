import pandas as pd
import streamlit as st

from attributes import KEYS, LABELS
from cars import DISPLAY_NAME
from ui.formatting import ATTRIBUTE_DECIMALS, style_numbers


def render_cars_table(cars: pd.DataFrame) -> None:
    columns = [DISPLAY_NAME, *KEYS]
    table = cars[columns].rename(columns=LABELS)

    st.dataframe(style_numbers(table, ATTRIBUTE_DECIMALS), hide_index=True, width="stretch")
