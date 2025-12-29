import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from webapp import app


class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Startup Profitability Simulator', r.data)

    def test_simulate_post(self):
        r = self.client.post('/simulate', data={
            'fixed_costs': '1000', 'price': '10', 'variable_cost': '5', 'initial_sales': '10', 'monthly_growth': '0.1', 'months': '6'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Projection Results', r.data)

    def test_cohort_routes(self):
        r = self.client.get('/cohort')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post('/cohort_simulate', data={'initial_customers': '50', 'monthly_margin': '5', 'monthly_churn': '0.1', 'months': '6'})
        self.assertEqual(r2.status_code, 200)
        self.assertIn(b'Cohort Analysis Results', r2.data)

    def test_compare(self):
        r = self.client.get('/compare')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post('/compare_simulate', data={'months': '6'})
        self.assertEqual(r2.status_code, 200)
        self.assertIn(b'Scenario Comparison', r2.data)

    def test_sensitivity_form(self):
        r = self.client.get('/sensitivity')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Sensitivity Analysis', r.data)

    def test_sensitivity_simulate(self):
        r = self.client.post('/sensitivity_simulate', data={
            'fixed_costs': '10000', 'price': '50', 'variable_cost': '20', 'initial_sales': '200',
            'monthly_growth': '0.05', 'months': '12', 'parameter': 'price', 'variation': '0.2'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Sensitivity Analysis:', r.data)

    def test_scenarios_list(self):
        r = self.client.get('/scenarios')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'Manage Scenarios', r.data)

    def test_save_scenario(self):
        r = self.client.post('/scenarios/save', data={
            'scenario_name': 'test_scenario', 'fixed_costs': '5000', 'price': '40',
            'variable_cost': '15', 'initial_sales': '100', 'monthly_growth': '0.03', 'months': '10'
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'test_scenario', r.data)


if __name__ == '__main__':
    unittest.main()
