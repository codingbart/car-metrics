"""The single definition of the car attributes that the application analyses.

The database schema, the statistics, the ranking, the input form and the
pictogram chart all read this module, so an attribute is changed here only.
Refer to one attribute by its constant (PRICE.unit, cars[PRICE.key]) rather
than by its key as a string.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Attribute:
    key: str  # column name in the database and in data frames
    name: str
    unit: str
    pictogram_unit: float  # how many units one pictogram icon stands for
    decimals: int = 0  # shown when a single value is displayed
    lower_is_better: bool = False
    allows_zero: bool = False

    @property
    def label(self) -> str:
        return f"{self.name} [{self.unit}]"


POWER = Attribute("power", "Moc", "KM", pictogram_unit=25)
FUEL = Attribute(
    "fuel",
    "Spalanie",
    "l/100 km",
    pictogram_unit=1,
    decimals=1,
    lower_is_better=True
)
TRUNK = Attribute("trunk", "Bagażnik", "l", pictogram_unit=100, allows_zero=True)
PRICE = Attribute("price", "Cena", "PLN", pictogram_unit=25000, lower_is_better=True)
ACCELERATION = Attribute(
    "acceleration",
    "Przyspieszenie 0-100 km/h",
    "s",
    pictogram_unit=1,
    decimals=1,
    lower_is_better=True
)

ATTRIBUTES: tuple[Attribute, ...] = (POWER, FUEL, TRUNK, PRICE, ACCELERATION)

KEYS: list[str] = [attribute.key for attribute in ATTRIBUTES]
LABELS: dict[str, str] = {attribute.key: attribute.label for attribute in ATTRIBUTES}
