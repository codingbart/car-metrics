# Car Metrics

Requirements: Task and Docker

Run from the project directory:

```sh
task dev
```

App: http://localhost:8501

`src/` and `data/` are mounted into the container, so saving a file reloads the app.
Changes to `requirements.txt` or `Dockerfile` need another `task dev`.

## Data

`data/qatarcars.csv` is the Qatar Cars dataset by Paul Musgrave (2025), licensed CC BY 4.0: https://github.com/profmusgrave/qatarcars

Citation: Paul Musgrave, "Defaulting to Inclusion: Producing Sample Datasets for the Global Data Science Classroom," Journal of Political Science Education, 2025, doi:10.1080/15512169.2025.2572320.

The app imports it automatically into an empty database:

- Electric cars are skipped, because the source has no fuel economy for them (95 of 105 cars remain).
- Prices are converted from Qatari riyals to PLN at the NBP mid rate of 1.1354 (table 002/B/NBP/2025, 2025-01-15).
- The fifth attribute is 0-100 km/h acceleration instead of top speed, which the dataset does not contain.

## Code

| Module | Responsibility |
| --- | --- |
| `src/attributes.py` | The single definition of the five analysed attributes |
| `src/analysis.py` | Distribution measures, correlations, ranking |
| `src/cars.py` | Car record type and display names |
| `src/dataset.py` | Qatar Cars import |
| `src/db.py`, `src/repository.py` | SQLite schema, connection and persistence |
| `src/ui/` | Streamlit page parts; `src/app.py` only lays them out |

Data is stored in a SQLite file, `cars.db`, inside the container. It is created and filled from the CSV when the app starts with an empty database; the CSV stays the source of truth.

To change an attribute, edit `src/attributes.py`, then run `task stop` and `task dev`, so the database is created again with the new columns.
