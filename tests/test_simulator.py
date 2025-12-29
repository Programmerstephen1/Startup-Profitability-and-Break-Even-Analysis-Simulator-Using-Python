import os
import sys
import unittest

# Ensure `src` is on path for imports when running tests from project root
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from simulator import break_even_units, project_months, break_even_month
from simulator import calculate_ltv, cac_payback_months


class SimulatorTests(unittest.TestCase):
    def test_break_even_units_basic(self):
        fixed = 1000
        price = 10
        var = 5
        be = break_even_units(fixed, price, var)
        self.assertAlmostEqual(be, 200.0)

    def test_break_even_units_error(self):
        with self.assertRaises(ValueError):
            break_even_units(100, 5, 5)

    def test_project_and_break_even_month(self):
        results = project_months(1000, 10, 5, initial_sales=20, monthly_growth=0.5, months=12)
        be_month = break_even_month(results)
        self.assertIsInstance(be_month, int)

    def test_ltv_and_cac_payback(self):
        ltv = calculate_ltv(monthly_margin_per_customer=10.0, monthly_churn_rate=0.2)
        self.assertAlmostEqual(ltv, 50.0)
        months = cac_payback_months(cac=200.0, monthly_margin_per_customer=10.0)
        self.assertEqual(months, 20)


if __name__ == '__main__':
    unittest.main()
