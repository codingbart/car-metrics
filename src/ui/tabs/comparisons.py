import pandas as pd
import plotly.express as px
import streamlit as st

from attributes import LABELS, POWER, PRICE
from cars import DISPLAY_NAME
from ui.formatting import PLOTLY_SEPARATORS
from ui.inputs import select_attribute
from ui.pictogram import render_pictogram


def render_comparisons(cars: pd.DataFrame) -> None:
    left, right = st.columns(2)

    with left:
        x_attribute = select_attribute("Oś X", default=PRICE)
    with right:
        y_attribute = select_attribute("Oś Y", default=POWER)

    scatter = px.scatter(
        cars,
        x=x_attribute.key,
        y=y_attribute.key,
        color="brand",
        hover_name=DISPLAY_NAME,
        labels=LABELS
    )
    scatter.update_layout(separators=PLOTLY_SEPARATORS)

    st.plotly_chart(scatter, width="stretch")

    render_pictogram(cars)
