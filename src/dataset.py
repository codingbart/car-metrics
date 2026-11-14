"""Qatar Cars (P. Musgrave, 2025, CC BY 4.0)"""
import csv
from datetime import date
from pathlib import Path

from attributes import ACCELERATION, FUEL, POWER, PRICE, TRUNK, Attribute
from cars import CarRecord
from repository import CarRepository

CSV_PATH = Path(__file__).parent.parent / "data" / "qatarcars.csv"
SOURCE_URL = "https://github.com/profmusgrave/qatarcars"
SOURCE_DATE = date(2026, 11, 14)
MODEL_YEAR = 2025
QAR_TO_PLN = 1.1354
SOURCE_COLUMNS: dict[Attribute, str] = {
    POWER: "horsepower",
    FUEL: "economy",
    TRUNK: "trunk",
    PRICE: "price",
    ACCELERATION: "performance"
}
ENGINE_NAMES = {"Petrol": "benzyna", "Hybrid": "hybryda", "Electric": "elektryczny"}


def convert_qar_to_pln(amount_qar: float) -> float:
    return float(round(amount_qar * QAR_TO_PLN))


def _convert_row(row: dict[str, str]) -> CarRecord:
    values = {
        attribute.key: float(row[column])
        for attribute, column in SOURCE_COLUMNS.items()
    }
    values[PRICE.key] = convert_qar_to_pln(values[PRICE.key])

    engine_name = ENGINE_NAMES.get(row["enginetype"], row["enginetype"])

    return dict(
        brand=row["make"],
        model=row["model"],
        variant=f"{row['type']}, {engine_name}",
        year=MODEL_YEAR,
        **values,
        source_url=SOURCE_URL,
        source_date=SOURCE_DATE
    )


def read_qatar_cars(path: Path = CSV_PATH) -> list[CarRecord]:
    with open(path, newline="", encoding="utf-8") as csv_file:
        rows = list(csv.DictReader(csv_file))

    rows_with_fuel_economy = [row for row in rows if row[SOURCE_COLUMNS[FUEL]].strip()]

    return [_convert_row(row) for row in rows_with_fuel_economy]


def import_qatar_cars(repository: CarRepository) -> None:
    repository.add_missing(read_qatar_cars())
