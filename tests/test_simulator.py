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
from simulator import cohort_projection, sensitivity_analysis


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

    def test_cohort_projection(self):
        results = cohort_projection(initial_customers=100, monthly_margin_per_customer=5.0, monthly_churn_rate=0.1, months=6)
        self.assertEqual(len(results), 6)
        # month 1 margin = 100 * 5 = 500
        self.assertAlmostEqual(results[0]['monthly_margin'], 500.0)
        # month 2 customers = 90 -> margin 450
        self.assertAlmostEqual(results[1]['monthly_margin'], 90 * 5.0)

    def test_sensitivity_analysis_price(self):
        results = sensitivity_analysis(fixed_costs=10000, price=50, variable_cost=20, initial_sales=200, 
                                       monthly_growth=0.05, months=12, parameter='price', variation_range=0.2)
        self.assertEqual(len(results), 5)
        # Center point (0% change) should exist
        center = [r for r in results if r['change_percent'] == 0][0]
        self.assertIsNotNone(center)
        # Results should have keys
        for r in results:
            self.assertIn('change_percent', r)
            self.assertIn('break_even_month', r)
            self.assertIn('final_cumulative_profit', r)

    def test_sensitivity_analysis_variable_cost(self):
        results = sensitivity_analysis(fixed_costs=10000, price=50, variable_cost=20, initial_sales=200, 
                                       monthly_growth=0.05, months=12, parameter='variable_cost', variation_range=0.1)
        self.assertEqual(len(results), 5)
        # Higher variable cost should reduce profit
        neg_10 = [r for r in results if r['change_percent'] == -10][0]
        pos_10 = [r for r in results if r['change_percent'] == 10][0]
        self.assertGreater(neg_10['final_cumulative_profit'], pos_10['final_cumulative_profit'])



if __name__ == '__main__':
    unittest.main()
