import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis

ATTRS = {"power": "Moc [KM]", "fuel": "Spalanie [l/100 km]",
         "trunk": "Bagażnik [l]", "price": "Cena [PLN]", "speed": "Prędkość [km/h]"}


def describe(frame):
    rows = {}
    for key, label in ATTRS.items():
        x = frame[key].dropna()
        n = len(x)
        variable = n > 1 and x.nunique() > 1
        modes = x.mode()
        rows[label] = {
            "N": n, "Średnia": x.mean(), "Mediana": x.median(),
            "Dominanta": ", ".join(f"{v:g}" for v in modes) if len(modes) < n else "Brak",
            "Minimum": x.min(), "Maksimum": x.max(), "Rozstęp": x.max() - x.min(),
            "Q1": x.quantile(.25), "Q3": x.quantile(.75),
            "IQR": x.quantile(.75) - x.quantile(.25),
            "Wariancja (próba)": x.var(ddof=1),
            "Odchylenie standardowe": x.std(ddof=1),
            "Współczynnik zmienności [%]": 100 * x.std(ddof=1) / x.mean() if n and x.mean() != 0 else np.nan,
            "Skośność": skew(x, bias=False) if n >= 3 and variable else np.nan,
            "Kurtoza nadmiarowa": kurtosis(x, fisher=True, bias=False) if n >= 4 and variable else np.nan,
        }
    return pd.DataFrame(rows).T


def correlations(frame, method="pearson"):
    return frame[list(ATTRS)].corr(method=method, min_periods=3).rename(index=ATTRS, columns=ATTRS)


def rank_cars(frame, weights):
    values = frame[list(ATTRS)].astype(float)
    spans = values.max() - values.min()
    scores = (values - values.min()) / spans.replace(0, np.nan)
    for key in ("fuel", "price"):
        scores[key] = 1 - scores[key]
    scores = scores.fillna(.5)
    w = pd.Series(weights).reindex(ATTRS).fillna(0)
    if w.sum() <= 0:
        raise ValueError("Ustaw przynajmniej jedną wagę większą od zera.")
    return frame.assign(wynik=(scores.mul(w).sum(axis=1) / w.sum() * 100)).sort_values("wynik", ascending=False)
