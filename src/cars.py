from typing import Any

import pandas as pd

DISPLAY_NAME = "Samochód"

# One row of the cars table, keyed by column name. The attribute columns come
# from attributes.ATTRIBUTES, so the keys cannot be listed statically here.
CarRecord = dict[str, Any]


def add_display_name(cars: pd.DataFrame) -> pd.DataFrame:
    name = cars.brand + " / " + cars.model + " / " + cars.variant + " / " + cars.year.astype(str)

    return cars.assign(**{DISPLAY_NAME: name})
