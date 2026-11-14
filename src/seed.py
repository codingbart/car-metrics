from datetime import date


def demo_cars():
    """Return deterministic fictional cars without accessing the database."""
    # Fictional objects: deterministic examples, never manufacturer specifications.
    rows = []
    for i in range(30):
        rows.append(dict(
            brand=["Demo City", "Demo Touring", "Demo Sport"][i % 3],
            model=f"Model {i + 1:02d}", variant="Benzyna — symulacja", year=2024,
            power=75 + i * 7, fuel=round(4.5 + i * .10 + (i % 4) * .3, 1),
            trunk=240 + (i * 37) % 400, price=65000 + i * 5600 + (i % 3) * 7000,
            speed=155 + i * 3, source_url="Dane syntetyczne — generator seed.py",
            source_date=date(2026, 10, 14), is_demo=True))
    return rows


def seed_demo(repository):
    """Insert demo records through the repository; repeated calls are safe."""
    repository.add_missing(demo_cars())
