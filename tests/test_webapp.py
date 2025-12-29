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
        self.assertIn(b'Cohort Results', r2.data)

    def test_compare(self):
        r = self.client.get('/compare')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post('/compare_simulate', data={'months': '6'})
        self.assertEqual(r2.status_code, 200)
        self.assertIn(b'Scenario Comparison', r2.data)


if __name__ == '__main__':
    unittest.main()
