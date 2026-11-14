import pandas as pd
import plotly.express as px
import streamlit as st

from analysis import CORRELATION_METHODS, correlate_attributes, find_strongest_correlation
from attributes import LABELS, PRICE
from cars import DISPLAY_NAME
from ui.formatting import PLOTLY_SEPARATORS, build_cell_formatter, format_number
from ui.inputs import choose_option


def _render_conclusions(cars: pd.DataFrame, matrix: pd.DataFrame) -> None:
    st.subheader("Wnioski z aktualnego wyboru")

    strongest = find_strongest_correlation(matrix)
    if strongest:
        first, second = strongest.attributes
        st.write(
            f"Największa bezwzględna korelacja: `{first.label} i {second.label}, "
            f"r = {format_number(strongest.coefficient, 3)} (n = {len(cars)})`."
        )
    else:
        st.info("Za mało zmiennych obserwacji do wyznaczenia korelacji.")

    prices = cars[PRICE.key]
    cheapest = cars.nsmallest(1, PRICE.key).iloc[0]
    price_range = prices.max() - prices.min()

    st.write(
        f"Najniższa cena: `{cheapest[DISPLAY_NAME]} - "
        f"{format_number(cheapest[PRICE.key], PRICE.decimals)} {PRICE.unit}`."
    )
    st.write(
        "Rozstęp cen w wyborze: "
        f"`{format_number(price_range, PRICE.decimals)} {PRICE.unit}`."
    )


def render_correlations(cars: pd.DataFrame) -> None:
    method = choose_option("Współczynnik", CORRELATION_METHODS)
    matrix = correlate_attributes(cars, method)
    labelled_matrix = matrix.rename(index=LABELS, columns=LABELS)

    heatmap = px.imshow(
        labelled_matrix,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        color_continuous_scale="RdBu",
        aspect="auto"
    )
    heatmap.update_layout(separators=PLOTLY_SEPARATORS)

    st.plotly_chart(heatmap, width="stretch")
    st.dataframe(labelled_matrix.style.format(build_cell_formatter(2)), width="stretch")

    _render_conclusions(cars, matrix)
