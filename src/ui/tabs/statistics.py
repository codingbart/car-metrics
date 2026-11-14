import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import describe
from attributes import LABELS
from ui.formatting import PLOTLY_SEPARATORS, style_statistics
from ui.inputs import select_attribute

ACCENT_COLOR = "#22c5a0"


def render_statistics(cars: pd.DataFrame) -> None:
    st.subheader("Rozkład pięciu parametrów")
    st.dataframe(style_statistics(describe(cars)), width="stretch")
    attribute = select_attribute("Parametr rozkładu")

    histogram = px.histogram(
        cars,
        x=attribute.key,
        marginal="box",
        labels=LABELS,
        color_discrete_sequence=[ACCENT_COLOR]
    )
    histogram.update_layout(separators=PLOTLY_SEPARATORS)

    st.plotly_chart(histogram, width="stretch")
