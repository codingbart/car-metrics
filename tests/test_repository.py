"""Portable repository tests; PostgreSQL-specific batch SQL is checked separately."""
import unittest
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import OperationalError

from db import initialize
from repository import CarRepository, InvalidCarError, RepositoryError
from seed import demo_cars, seed_demo


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        initialize(self.engine)
        self.repository = CarRepository(self.engine)

    def tearDown(self):
        self.engine.dispose()

    def test_empty_result_preserves_columns(self):
        result = self.repository.list_all()
        self.assertTrue(result.empty)
        self.assertIn("price", result.columns)
        self.assertIn("is_demo", result.columns)

    def test_round_trip(self):
        row = demo_cars()[0]
        self.repository.add(row)
        saved = self.repository.list_all().iloc[0]
        for key, value in row.items():
            self.assertEqual(saved[key], value)

    def test_duplicate_rollback_allows_next_write(self):
        first, second = demo_cars()[:2]
        self.repository.add(first)
        with self.assertRaises(InvalidCarError):
            self.repository.add(first)
        self.repository.add(second)
        self.assertEqual(len(self.repository.list_all()), 2)

    def test_invalid_parameter_is_not_saved(self):
        row = dict(demo_cars()[0], power=-1)
        with self.assertRaises(InvalidCarError):
            self.repository.add(row)
        self.assertTrue(self.repository.list_all().empty)

    def test_connection_failure_is_translated(self):
        engine = MagicMock()
        engine.connect.side_effect = OperationalError("connect", {}, Exception("offline"))
        with self.assertRaises(RepositoryError):
            CarRepository(engine).list_all()

    def test_batch_targets_postgres_identity_constraint(self):
        engine = MagicMock()
        repository = CarRepository(engine)
        repository.add_missing(demo_cars())
        statement = engine.begin.return_value.__enter__.return_value.execute.call_args.args[0]
        sql = str(statement.compile(dialect=postgresql.dialect()))
        self.assertIn("ON CONFLICT ON CONSTRAINT car_identity DO NOTHING", sql)

    def test_empty_batch_does_not_connect(self):
        engine = MagicMock()
        CarRepository(engine).add_missing([])
        engine.begin.assert_not_called()


class SeedTests(unittest.TestCase):
    def test_demo_data_is_deterministic_and_unique(self):
        rows = demo_cars()
        self.assertEqual(rows, demo_cars())
        self.assertEqual(len(rows), 30)
        self.assertEqual(len({(r['brand'], r['model'], r['variant'], r['year']) for r in rows}), 30)
        self.assertTrue(all(r['is_demo'] for r in rows))

    def test_seed_can_use_an_injected_repository(self):
        repository = MagicMock(spec=CarRepository)
        seed_demo(repository)
        repository.add_missing.assert_called_once_with(demo_cars())


if __name__ == '__main__':
    unittest.main()
