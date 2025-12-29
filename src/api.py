"""REST API endpoints for the Startup Simulator."""
from flask import Blueprint, request, jsonify
from simulator import project_months, cohort_projection, sensitivity_analysis, break_even_month
from scenarios import save_scenario, load_scenario, list_scenarios, delete_scenario

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/project', methods=['GET'])
def api_project():
    """
    Run a projection simulation.
    
    Query Parameters:
    - fixed_costs (float): Fixed costs
    - price (float): Price per unit
    - variable_cost (float): Variable cost per unit
    - initial_sales (int): Initial sales/units
    - monthly_growth (float): Monthly growth rate (0-1)
    - months (int): Number of months to project
    """
    try:
        fixed_costs = float(request.args.get('fixed_costs', 10000))
        price = float(request.args.get('price', 50))
        variable_cost = float(request.args.get('variable_cost', 20))
        initial_sales = int(request.args.get('initial_sales', 200))
        monthly_growth = float(request.args.get('monthly_growth', 0.05))
        months = int(request.args.get('months', 12))

        results = project_months(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months)
        be_month = break_even_month(results)

        return jsonify({
            'status': 'success',
            'data': {
                'results': results,
                'break_even_month': be_month,
                'final_cumulative_profit': results[-1]['cumulative_profit'] if results else 0,
            }
        })
    except (ValueError, TypeError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/cohort', methods=['GET'])
def api_cohort():
    """
    Run a cohort projection.
    
    Query Parameters:
    - initial_customers (int): Initial customer count
    - monthly_margin (float): Monthly margin per customer
    - monthly_churn (float): Monthly churn rate (0-1)
    - months (int): Number of months to project
    """
    try:
        initial_customers = int(request.args.get('initial_customers', 100))
        monthly_margin = float(request.args.get('monthly_margin', 5.0))
        monthly_churn = float(request.args.get('monthly_churn', 0.1))
        months = int(request.args.get('months', 12))

        results = cohort_projection(initial_customers, monthly_margin, monthly_churn, months)

        return jsonify({
            'status': 'success',
            'data': {
                'results': results,
                'final_cumulative_margin': results[-1]['cumulative_margin'] if results else 0,
            }
        })
    except (ValueError, TypeError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/sensitivity', methods=['GET'])
def api_sensitivity():
    """
    Run sensitivity analysis.
    
    Query Parameters:
    - fixed_costs (float): Fixed costs
    - price (float): Price per unit
    - variable_cost (float): Variable cost per unit
    - initial_sales (int): Initial sales
    - monthly_growth (float): Monthly growth rate
    - months (int): Number of months
    - parameter (str): Parameter to vary (price, variable_cost, initial_sales, monthly_growth, fixed_costs)
    - variation (float): Variation range (e.g., 0.2 for ±20%)
    """
    try:
        fixed_costs = float(request.args.get('fixed_costs', 10000))
        price = float(request.args.get('price', 50))
        variable_cost = float(request.args.get('variable_cost', 20))
        initial_sales = int(request.args.get('initial_sales', 200))
        monthly_growth = float(request.args.get('monthly_growth', 0.05))
        months = int(request.args.get('months', 12))
        parameter = request.args.get('parameter', 'price')
        variation = float(request.args.get('variation', 0.2))

        results = sensitivity_analysis(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months, parameter, variation)

        return jsonify({
            'status': 'success',
            'data': {
                'parameter': parameter,
                'variation_range': variation,
                'results': results,
            }
        })
    except (ValueError, TypeError) as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/scenarios', methods=['GET'])
def api_scenarios_list():
    """List all saved scenarios."""
    try:
        scenario_names = list_scenarios()
        return jsonify({
            'status': 'success',
            'data': {
                'scenarios': scenario_names,
                'count': len(scenario_names),
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/scenarios', methods=['POST'])
def api_save_scenario():
    """
    Save a scenario.
    
    JSON Body:
    {
        "name": "scenario_name",
        "fixed_costs": 10000,
        "price": 50,
        "variable_cost": 20,
        "initial_sales": 200,
        "monthly_growth": 0.05,
        "months": 12
    }
    """
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'status': 'error', 'message': 'Missing scenario name'}), 400

        name = data['name']
        params = {
            'fixed_costs': float(data.get('fixed_costs', 10000)),
            'price': float(data.get('price', 50)),
            'variable_cost': float(data.get('variable_cost', 20)),
            'initial_sales': int(data.get('initial_sales', 200)),
            'monthly_growth': float(data.get('monthly_growth', 0.05)),
            'months': int(data.get('months', 12)),
        }

        save_scenario(name, params)

        return jsonify({
            'status': 'success',
            'message': f'Scenario "{name}" saved successfully',
            'data': {'name': name}
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/scenarios/<scenario_name>', methods=['GET'])
def api_load_scenario(scenario_name):
    """Load a saved scenario."""
    try:
        params = load_scenario(scenario_name)
        return jsonify({
            'status': 'success',
            'data': {
                'name': scenario_name,
                'params': params,
            }
        })
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': f'Scenario "{scenario_name}" not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/scenarios/<scenario_name>', methods=['DELETE'])
def api_delete_scenario(scenario_name):
    """Delete a saved scenario."""
    try:
        if delete_scenario(scenario_name):
            return jsonify({
                'status': 'success',
                'message': f'Scenario "{scenario_name}" deleted successfully',
            })
        else:
            return jsonify({'status': 'error', 'message': f'Scenario "{scenario_name}" not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@api.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Startup Simulator API',
        'version': '1.0.0',
    })
