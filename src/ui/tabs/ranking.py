import pandas as pd
import streamlit as st

from analysis import SCORE, rank_cars
from attributes import ATTRIBUTES, KEYS, LABELS
from cars import DISPLAY_NAME
from ui.formatting import ATTRIBUTE_DECIMALS, style_numbers

MAX_WEIGHT = 10
DEFAULT_WEIGHT = 5
SCORE_COLUMN = "Wynik / 100"
SCORE_DECIMALS = 1


def _describe_ranking_directions() -> str:
    lower_is_better = ", ".join(f"`{a.label}`" for a in ATTRIBUTES if a.lower_is_better)
    higher_is_better = ", ".join(f"`{a.label}`" for a in ATTRIBUTES if not a.lower_is_better)

    # Two trailing spaces end a line in markdown without starting a new paragraph.
    return (
        "Ustaw wagi, według których zostanie ułożony ranking.  \n"
        f"Im mniej, tym lepiej: {lower_is_better}  \n"
        f"Im więcej, tym lepiej: {higher_is_better}"
    )


def render_ranking(cars: pd.DataFrame) -> None:
    st.subheader("Ranking samochodów")
    st.caption("Ranking ustalany jest według ważonej średniej po normalizacji min-max w aktualnym wyborze.")
    st.write(_describe_ranking_directions())

    weights = {
        attribute.key: column.slider(attribute.label, 0, MAX_WEIGHT, DEFAULT_WEIGHT)
        for column, attribute in zip(st.columns(len(ATTRIBUTES)), ATTRIBUTES)
    }

    if sum(weights.values()):
        ranked = rank_cars(cars, weights)
        columns = [DISPLAY_NAME, SCORE, *KEYS]
        table = ranked[columns].rename(columns={**LABELS, SCORE: SCORE_COLUMN})
        styled_table = style_numbers(
            table,
            {**ATTRIBUTE_DECIMALS, SCORE_COLUMN: SCORE_DECIMALS}
        )

        st.dataframe(styled_table, hide_index=True, width="stretch")
    else:
        st.info("Ustaw przynajmniej jedną wagę większą od zera.")
