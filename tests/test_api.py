import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.webapp import app


class APITests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('service', data)

    def test_project_api_get(self):
        response = self.client.get('/api/project?fixed_costs=10000&price=50&variable_cost=20&initial_sales=200&monthly_growth=0.05&months=12')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('data', data)
        self.assertIn('results', data['data'])
        self.assertIn('break_even_month', data['data'])

    def test_project_api_invalid_params(self):
        response = self.client.get('/api/project?fixed_costs=invalid')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['status'], 'error')

    def test_cohort_api_get(self):
        response = self.client.get('/api/cohort?initial_customers=100&monthly_margin=5.0&monthly_churn=0.1&months=12')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('results', data['data'])

    def test_sensitivity_api_get(self):
        response = self.client.get('/api/sensitivity?parameter=price&variation=0.2')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['parameter'], 'price')

    def test_scenarios_list_api(self):
        response = self.client.get('/api/scenarios')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('scenarios', data['data'])
        self.assertIn('count', data['data'])

    def test_save_scenario_api(self):
        scenario_data = {
            'name': 'api_test_scenario',
            'fixed_costs': 10000,
            'price': 50,
            'variable_cost': 20,
            'initial_sales': 200,
            'monthly_growth': 0.05,
            'months': 12,
        }
        response = self.client.post('/api/scenarios', json=scenario_data)
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['name'], 'api_test_scenario')

    def test_load_scenario_api(self):
        # Save first
        scenario_data = {
            'name': 'api_load_test',
            'fixed_costs': 12000,
            'price': 60,
            'variable_cost': 25,
            'initial_sales': 300,
            'monthly_growth': 0.08,
            'months': 15,
        }
        self.client.post('/api/scenarios', json=scenario_data)

        # Load
        response = self.client.get('/api/scenarios/api_load_test')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['params']['price'], 60)

    def test_load_nonexistent_scenario(self):
        response = self.client.get('/api/scenarios/nonexistent_scenario_xyz')
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['status'], 'error')

    def test_delete_scenario_api(self):
        # Save first
        scenario_data = {'name': 'api_delete_test', 'fixed_costs': 10000, 'price': 50}
        self.client.post('/api/scenarios', json=scenario_data)

        # Delete
        response = self.client.delete('/api/scenarios/api_delete_test')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')

        # Verify deleted
        response = self.client.get('/api/scenarios/api_delete_test')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
