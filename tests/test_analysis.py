import unittest
import numpy as np
import pandas as pd
from analysis import ATTRS, describe, correlations, rank_cars

class AnalysisTests(unittest.TestCase):
    def test_known_statistics(self):
        frame = pd.DataFrame({k: [1., 2., 3., 4.] for k in ATTRS})
        result = describe(frame).iloc[0]
        self.assertEqual(result['Średnia'], 2.5)
        self.assertAlmostEqual(result['Wariancja (próba)'], 5/3)
        self.assertAlmostEqual(result['Skośność'], 0)
        self.assertAlmostEqual(result['Kurtoza nadmiarowa'], -1.2)
        self.assertEqual(result['Dominanta'], 'Brak')
        self.assertTrue(np.allclose(correlations(frame), 1))

    def test_constant_and_single(self):
        frame = pd.DataFrame({k: [3.] for k in ATTRS})
        self.assertTrue(np.isnan(describe(frame).iloc[0]['Skośność']))
        self.assertTrue(correlations(frame).isna().all().all())
        self.assertEqual(rank_cars(frame, dict.fromkeys(ATTRS, 1)).wynik.iloc[0], 50)

    def test_price_direction_and_zero_weights(self):
        frame = pd.DataFrame({k: [1., 2., 3.] for k in ATTRS})
        self.assertEqual(rank_cars(frame, {'price': 1}).index[0], 0)
        self.assertEqual(rank_cars(frame, {'power': 1}).index[0], 2)
        with self.assertRaises(ValueError):
            rank_cars(frame, dict.fromkeys(ATTRS, 0))

if __name__ == '__main__':
    unittest.main()
