import math
from collections.abc import Callable, Mapping
from numbers import Real

import pandas as pd
from pandas.io.formats.style import Styler

from attributes import ATTRIBUTES

UNDEFINED = "-"
NO_MODE = "Brak"
STATISTIC_DECIMALS = 2
# Plotly's decimal and thousands separators, in that order.
PLOTLY_SEPARATORS = ", "

ATTRIBUTE_DECIMALS: dict[str, int] = {
    attribute.label: attribute.decimals
    for attribute in ATTRIBUTES
}


def format_number(value: float, decimals: int = 2) -> str:
    if math.isnan(value):
        return UNDEFINED

    english = f"{value:,.{decimals}f}"

    return english.replace(",", " ").replace(".", ",")


def build_cell_formatter(decimals: int) -> Callable[[object], str]:
    def format_cell(value: object) -> str:
        if not isinstance(value, Real):
            return str(value)

        return format_number(float(value), decimals)

    return format_cell


def _format_statistic(value: object) -> str:
    if isinstance(value, tuple):
        modes = [format_number(mode, STATISTIC_DECIMALS) for mode in value]
        return "; ".join(modes) if modes else NO_MODE

    return build_cell_formatter(STATISTIC_DECIMALS)(value)


def style_statistics(table: pd.DataFrame) -> Styler:
    return table.style.format(_format_statistic)


def style_numbers(table: pd.DataFrame, decimals_by_column: Mapping[str, int]) -> Styler:
    # Typed as Styler.format expects; a dict is invariant in its value type.
    formatters: dict[str, str | Callable[[object], str] | None] = {
        column: build_cell_formatter(decimals)
        for column, decimals in decimals_by_column.items()
    }

    return table.style.format(formatters)
