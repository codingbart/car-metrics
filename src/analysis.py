"""Distribution measures, correlations, ranking and conclusions for a table of cars."""
from collections.abc import Mapping
from typing import Literal, NamedTuple

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew

from attributes import ATTRIBUTES, KEYS, Attribute

MIN_VALUES_FOR_SKEWNESS = 3
MIN_VALUES_FOR_KURTOSIS = 4
MIN_CARS_FOR_CORRELATION = 3
NEUTRAL_SCORE = .5
SCORE = "wynik"

CorrelationMethod = Literal["pearson", "spearman"]
CORRELATION_METHODS: tuple[CorrelationMethod, ...] = ("pearson", "spearman")


class Correlation(NamedTuple):
    attributes: tuple[Attribute, Attribute]
    coefficient: float


def _find_modes(values: pd.Series) -> tuple[float, ...]:
    # When no value repeats, every value is a mode; report none instead.
    modes = values.mode()
    every_value_is_unique = len(modes) == len(values)

    return () if every_value_is_unique else tuple(float(mode) for mode in modes)


def _describe_values(values: pd.Series) -> dict[str, float | tuple[float, ...]]:
    count = len(values)
    varies = count > 1 and values.nunique() > 1

    mean = values.mean()
    deviation = values.std(ddof=1)
    first_quartile = values.quantile(.25)
    third_quartile = values.quantile(.75)
    variation = 100 * deviation / mean if count and mean != 0 else np.nan

    has_skewness = count >= MIN_VALUES_FOR_SKEWNESS and varies
    has_kurtosis = count >= MIN_VALUES_FOR_KURTOSIS and varies
    skewness = skew(values, bias=False) if has_skewness else np.nan
    excess_kurtosis = kurtosis(values, fisher=True, bias=False) if has_kurtosis else np.nan

    return {
        "Średnia": mean,
        "Mediana": values.median(),
        "Dominanta": _find_modes(values),
        "Minimum": values.min(),
        "Maksimum": values.max(),
        "Rozstęp": values.max() - values.min(),
        "Q1": first_quartile,
        "Q3": third_quartile,
        "IQR": third_quartile - first_quartile,
        "Wariancja (próba)": values.var(ddof=1),
        "Odchylenie standardowe": deviation,
        "Współczynnik zmienności [%]": variation,
        "Skośność": skewness,
        "Kurtoza nadmiarowa": excess_kurtosis
    }


def describe(cars: pd.DataFrame) -> pd.DataFrame:
    measures_by_label = {
        attribute.label: _describe_values(cars[attribute.key].dropna())
        for attribute in ATTRIBUTES
    }

    return pd.DataFrame(measures_by_label).T


def correlate_attributes(
    cars: pd.DataFrame,
    method: CorrelationMethod = "pearson"
) -> pd.DataFrame:
    return cars[KEYS].corr(method=method, min_periods=MIN_CARS_FOR_CORRELATION)


def find_strongest_correlation(matrix: pd.DataFrame) -> Correlation | None:
    coefficients = matrix.reindex(index=KEYS, columns=KEYS).to_numpy(dtype=float)

    pairs = [
        Correlation(
            attributes=(ATTRIBUTES[row], ATTRIBUTES[column]),
            coefficient=float(coefficients[row, column])
        )
        for row in range(len(ATTRIBUTES))
        for column in range(row + 1, len(ATTRIBUTES))
    ]
    defined_pairs = [pair for pair in pairs if not np.isnan(pair.coefficient)]
    if not defined_pairs:
        return None

    return max(defined_pairs, key=lambda pair: abs(pair.coefficient))


def _score_attributes(values: pd.DataFrame) -> pd.DataFrame:
    spans = values.max() - values.min()
    scores = (values - values.min()) / spans.replace(0, np.nan)

    for attribute in ATTRIBUTES:
        if attribute.lower_is_better:
            scores[attribute.key] = 1 - scores[attribute.key]

    return scores.fillna(NEUTRAL_SCORE)


def rank_cars(cars: pd.DataFrame, weights: Mapping[str, float]) -> pd.DataFrame:
    weight_by_key = pd.Series(weights, dtype=float).reindex(KEYS).fillna(0)
    if weight_by_key.sum() <= 0:
        raise ValueError("Ustaw przynajmniej jedną wagę większą od zera.")

    scores = _score_attributes(cars[KEYS].astype(float))
    weighted_average = scores.mul(weight_by_key).sum(axis=1) / weight_by_key.sum()

    return cars.assign(**{SCORE: weighted_average * 100}).sort_values(SCORE, ascending=False)
