"""The five tabs of the main area, each drawn from the filtered cars."""
from collections.abc import Callable

import pandas as pd
import streamlit as st

from ui.tabs.cars_table import render_cars_table
from ui.tabs.comparisons import render_comparisons
from ui.tabs.correlations import render_correlations
from ui.tabs.ranking import render_ranking
from ui.tabs.statistics import render_statistics

TABS: dict[str, Callable[[pd.DataFrame], None]] = {
    "Samochody": render_cars_table,
    "Statystyki": render_statistics,
    "Porównania": render_comparisons,
    "Korelacje": render_correlations,
    "Ranking": render_ranking
}


def render_tabs(cars: pd.DataFrame) -> None:
    for tab, render_tab in zip(st.tabs(list(TABS)), TABS.values()):
        with tab:
            render_tab(cars)
