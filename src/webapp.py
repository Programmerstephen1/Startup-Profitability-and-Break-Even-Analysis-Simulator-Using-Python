from flask import Flask, request, render_template_string, url_for
import json
from simulator import project_months, cohort_projection, sensitivity_analysis
from scenarios import save_scenario, load_scenario, list_scenarios, delete_scenario
from api import api
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.register_blueprint(api)

# Base HTML template with header and navigation
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Profitability Simulator</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>📊 Startup Profitability Simulator</h1>
            <p>Analyze financial projections, break-even points, and business scenarios</p>
            <nav>
                <a href="/">Dashboard</a>
                <a href="/sensitivity">Sensitivity Analysis</a>
                <a href="/cohort">Cohort Projection</a>
                <a href="/compare">Compare Scenarios</a>
                <a href="/scenarios">Manage Scenarios</a>
            </nav>
        </div>
    </header>
    <main class="container">
        {content}
    </main>
    <footer>
        <p>&copy; 2025 Startup Simulator. Built with Python, Flask, and ❤️</p>
    </footer>
</body>
</html>
'''

TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>${revenue:,.0f}</td><td>${variable_costs:,.0f}</td><td>${profit:,.0f}</td><td>${cumulative_profit:,.0f}</td></tr>"

TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>${revenue:,.0f}</td><td>${variable_costs:,.0f}</td><td>${profit:,.0f}</td><td>${cumulative_profit:,.0f}</td></tr>"

@app.route('/')
def index():
    content = '''
    <div class="grid-2">
        <div class="card">
            <h3>📈 Quick Projection</h3>
            <p>Model your startup's profitability over time. Enter your business parameters and see when you'll break even.</p>
            <form action="/simulate" method="post">
                <div class="form-group">
                    <label>Fixed Costs</label>
                    <input type="number" name="fixed_costs" value="10000" step="100">
                </div>
                <div class="form-group">
                    <label>Price per Unit</label>
                    <input type="number" name="price" value="50" step="0.01">
                </div>
                <div class="form-group">
                    <label>Variable Cost per Unit</label>
                    <input type="number" name="variable_cost" value="20" step="0.01">
                </div>
                <div class="form-group">
                    <label>Initial Sales (units)</label>
                    <input type="number" name="initial_sales" value="200" step="1">
                </div>
                <div class="form-group">
                    <label>Monthly Growth Rate</label>
                    <input type="number" name="monthly_growth" value="0.05" step="0.01" min="0" max="1">
                </div>
                <div class="form-group">
                    <label>Number of Months</label>
                    <input type="number" name="months" value="12" step="1" min="1">
                </div>
                <button type="submit">Run Projection</button>
            </form>
        </div>

        <div class="card">
            <h3>ℹ️ What This Does</h3>
            <p><strong>Projection:</strong> Simulates monthly revenue, costs, and cumulative profit based on your inputs.</p>
            <p><strong>Break-even:</strong> Identifies the month when cumulative profit becomes positive.</p>
            <p><strong>Sensitivity:</strong> Analyzes how changes to key parameters affect outcomes.</p>
            <p><strong>Scenarios:</strong> Save and compare different business models.</p>
            <hr class="divider">
            <p><strong>Tip:</strong> Use different scenarios to explore pricing strategies, cost structures, and growth rates.</p>
        </div>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/simulate', methods=['POST'])
def simulate():
    fixed_costs = float(request.form.get('fixed_costs', 10000))
    price = float(request.form.get('price', 50))
    variable_cost = float(request.form.get('variable_cost', 20))
    initial_sales = int(request.form.get('initial_sales', 200))
    monthly_growth = float(request.form.get('monthly_growth', 0.05))
    months = int(request.form.get('months', 12))

    results = project_months(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months)
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    
    # Calculate metrics
    from simulator import break_even_month
    be_month = break_even_month(results)
    final_profit = results[-1]['cumulative_profit']
    
    content = f'''
    <a href="/" class="back-link">← Back to Dashboard</a>
    
    <div class="card">
        <h2>📊 Projection Results</h2>
        <div class="grid-2">
            <div>
                <h4>Break-Even Month</h4>
                <p style="font-size: 24px; color: var(--primary-color); font-weight: bold;">
                    {be_month if be_month > 0 else "Not reached"}
                </p>
            </div>
            <div>
                <h4>Final Cumulative Profit</h4>
                <p style="font-size: 24px; color: var(--success-color); font-weight: bold;">
                    ${final_profit:,.0f}
                </p>
            </div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Month</th>
                <th>Units Sold</th>
                <th>Revenue</th>
                <th>Variable Costs</th>
                <th>Monthly Profit</th>
                <th>Cumulative Profit</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    
    <div class="btn-group">
        <a href="/" class="back-link">← Dashboard</a>
        <form action="/sensitivity" method="get" style="display: inline;">
            <button type="submit" class="btn-secondary">Run Sensitivity Analysis</button>
        </form>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/cohort')
def cohort_form():
    content = '''
    <a href="/" class="back-link">← Back to Dashboard</a>
    <form action="/cohort_simulate" method="post">
        <h2>🎯 Cohort Projection</h2>
        <p class="text-muted">Analyze how a single customer cohort evolves over time with churn and lifetime value.</p>
        
        <div class="form-group">
            <label>Initial Customers</label>
            <input type="number" name="initial_customers" value="100" step="1" min="1">
        </div>
        <div class="form-group">
            <label>Monthly Margin per Customer ($)</label>
            <input type="number" name="monthly_margin" value="5" step="0.01">
        </div>
        <div class="form-group">
            <label>Monthly Churn Rate (%)</label>
            <input type="number" name="monthly_churn" value="0.1" step="0.01" min="0" max="1">
        </div>
        <div class="form-group">
            <label>Months to Project</label>
            <input type="number" name="months" value="12" step="1" min="1">
        </div>
        <button type="submit">Run Cohort Analysis</button>
    </form>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/cohort_simulate', methods=['POST'])
def cohort_simulate():
    initial = int(request.form.get('initial_customers', 100))
    monthly_margin = float(request.form.get('monthly_margin', 5.0))
    monthly_churn = float(request.form.get('monthly_churn', 0.1))
    months = int(request.form.get('months', 12))

    results = cohort_projection(initial, monthly_margin, monthly_churn, months)
    rows = ''.join(f"<tr><td>{r['month']}</td><td>{r['customers']:,}</td><td>${r['monthly_margin']:,.0f}</td><td>${r['cumulative_margin']:,.0f}</td></tr>" for r in results)
    
    content = f'''
    <a href="/cohort" class="back-link">← Back</a>
    <div class="card">
        <h2>📈 Cohort Analysis Results</h2>
        <p>Shows customer retention and cumulative value generated from initial cohort of {initial} customers.</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Month</th>
                <th>Active Customers</th>
                <th>Monthly Margin</th>
                <th>Cumulative Margin</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    
    <div class="btn-group">
        <a href="/cohort" class="back-link">← Back</a>
        <a href="/" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/compare')
def compare_form():
    content = '''
    <a href="/" class="back-link">← Back to Dashboard</a>
    <form action="/compare_simulate" method="post">
        <h2>⚖️ Scenario Comparison</h2>
        <p class="text-muted">Compare two different business scenarios side-by-side to make informed decisions.</p>
        
        <div class="form-group">
            <label>Months to Project</label>
            <input type="number" name="months" value="12" step="1" min="1">
        </div>
        <button type="submit">Compare Default Scenarios</button>
    </form>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/compare_simulate', methods=['POST'])
def compare_simulate():
    months = int(request.form.get('months', 12))
    # Simple compare: use two different defaults
    a_results = project_months(10000, 50, 20, 200, 0.05, months)
    b_results = project_months(12000, 55, 22, 180, 0.06, months)
    rows_a = ''.join(TABLE_ROW.format(**r) for r in a_results)
    rows_b = ''.join(TABLE_ROW.format(**r) for r in b_results)
    
    content = f'''
    <a href="/compare" class="back-link">← Back</a>
    <h2>⚖️ Scenario Comparison</h2>
    
    <div class="grid-2">
        <div class="card">
            <h3>Scenario A</h3>
            <p><strong>Fixed Costs:</strong> $10,000</p>
            <p><strong>Price:</strong> $50</p>
            <p><strong>Variable Cost:</strong> $20</p>
            <p><strong>Initial Sales:</strong> 200 units</p>
            <p><strong>Growth:</strong> 5% per month</p>
        </div>
        <div class="card">
            <h3>Scenario B</h3>
            <p><strong>Fixed Costs:</strong> $12,000</p>
            <p><strong>Price:</strong> $55</p>
            <p><strong>Variable Cost:</strong> $22</p>
            <p><strong>Initial Sales:</strong> 180 units</p>
            <p><strong>Growth:</strong> 6% per month</p>
        </div>
    </div>

    <h3>Scenario A Results</h3>
    <table>
        <thead>
            <tr>
                <th>Month</th><th>Units</th><th>Revenue</th><th>Variable Costs</th><th>Profit</th><th>Cumulative</th>
            </tr>
        </thead>
        <tbody>
            {rows_a}
        </tbody>
    </table>

    <h3 style="margin-top: 30px;">Scenario B Results</h3>
    <table>
        <thead>
            <tr>
                <th>Month</th><th>Units</th><th>Revenue</th><th>Variable Costs</th><th>Profit</th><th>Cumulative</th>
            </tr>
        </thead>
        <tbody>
            {rows_b}
        </tbody>
    </table>
    
    <div class="btn-group" style="margin-top: 30px;">
        <a href="/compare" class="back-link">← Back</a>
        <a href="/" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/sensitivity')
def sensitivity_form():
    content = '''
    <a href="/" class="back-link">← Back to Dashboard</a>
    <form action="/sensitivity_simulate" method="post">
        <h2>🔍 Sensitivity Analysis</h2>
        <p class="text-muted">Analyze how changes in key parameters affect break-even month and final profit.</p>
        
        <h3>Business Parameters</h3>
        <div class="form-group">
            <label>Fixed Costs</label>
            <input type="number" name="fixed_costs" value="10000" step="100">
        </div>
        <div class="form-group">
            <label>Price per Unit</label>
            <input type="number" name="price" value="50" step="0.01">
        </div>
        <div class="form-group">
            <label>Variable Cost per Unit</label>
            <input type="number" name="variable_cost" value="20" step="0.01">
        </div>
        <div class="form-group">
            <label>Initial Sales (units)</label>
            <input type="number" name="initial_sales" value="200" step="1">
        </div>
        <div class="form-group">
            <label>Monthly Growth Rate</label>
            <input type="number" name="monthly_growth" value="0.05" step="0.01">
        </div>
        <div class="form-group">
            <label>Months</label>
            <input type="number" name="months" value="12" step="1" min="1">
        </div>

        <h3>Sensitivity Settings</h3>
        <div class="form-group">
            <label>Parameter to Vary</label>
            <select name="parameter">
                <option value="price">Price per Unit</option>
                <option value="variable_cost">Variable Cost per Unit</option>
                <option value="initial_sales">Initial Sales</option>
                <option value="monthly_growth">Monthly Growth Rate</option>
                <option value="fixed_costs">Fixed Costs</option>
            </select>
        </div>
        <div class="form-group">
            <label>Variation Range (e.g., 0.2 for ±20%)</label>
            <input type="number" name="variation" value="0.2" step="0.05" min="0" max="1">
        </div>
        <button type="submit">Run Sensitivity Analysis</button>
    </form>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/sensitivity_simulate', methods=['POST'])
def sensitivity_simulate():
    fixed_costs = float(request.form.get('fixed_costs', 10000))
    price = float(request.form.get('price', 50))
    variable_cost = float(request.form.get('variable_cost', 20))
    initial_sales = int(request.form.get('initial_sales', 200))
    monthly_growth = float(request.form.get('monthly_growth', 0.05))
    months = int(request.form.get('months', 12))
    parameter = request.form.get('parameter', 'price')
    variation = float(request.form.get('variation', 0.2))

    results = sensitivity_analysis(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months, parameter, variation)
    
    rows = ''.join(f"<tr><td style='font-weight: 600;'>{r['change_percent']:+d}%</td><td>{r['break_even_month']}</td><td>${r['final_cumulative_profit']:,.0f}</td></tr>" for r in results)
    
    content = f'''
    <a href="/sensitivity" class="back-link">← Back</a>
    <div class="card">
        <h2>🔍 Sensitivity Analysis: {parameter.replace("_", " ").title()}</h2>
        <p>Shows how ±{int(variation*100)}% changes to <strong>{parameter.replace("_", " ")}</strong> affect your business outcomes.</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Change</th>
                <th>Break-Even Month</th>
                <th>Final Profit</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    
    <div class="alert alert-info">
        <strong>💡 Insight:</strong> Larger changes in break-even month and profit indicate higher sensitivity to this parameter.
    </div>
    
    <div class="btn-group">
        <a href="/sensitivity" class="back-link">Run Another</a>
        <a href="/" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/scenarios')
def scenarios_list():
    scenario_names = list_scenarios()
    scenario_items = ''.join(f"<tr><td><strong>{name}</strong></td><td><a href='/scenarios/delete/{name}' class='btn-sm' onclick=\"return confirm('Delete scenario \\'{name}\\'?')\">Delete</a></td></tr>" for name in scenario_names)
    scenarios_table = f"<table><thead><tr><th>Scenario Name</th><th>Action</th></tr></thead><tbody>{scenario_items}</tbody></table>" if scenario_names else "<p class='text-muted'>No scenarios saved yet.</p>"
    
    content = f'''
    <a href="/" class="back-link">← Back to Dashboard</a>
    
    <h2>💾 Manage Scenarios</h2>
    <p>Save your business models and compare them later.</p>

    <div class="grid-2">
        <div>
            <div class="card">
                <h3>Saved Scenarios</h3>
                {scenarios_table}
            </div>
        </div>

        <div>
            <form action="/scenarios/save" method="post">
                <h3>Save New Scenario</h3>
                <div class="form-group">
                    <label>Scenario Name</label>
                    <input type="text" name="scenario_name" placeholder="e.g., Conservative Plan" required>
                </div>
                <h4>Parameters</h4>
                <div class="form-group">
                    <label>Fixed Costs</label>
                    <input type="number" name="fixed_costs" value="10000" step="100">
                </div>
                <div class="form-group">
                    <label>Price per Unit</label>
                    <input type="number" name="price" value="50" step="0.01">
                </div>
                <div class="form-group">
                    <label>Variable Cost per Unit</label>
                    <input type="number" name="variable_cost" value="20" step="0.01">
                </div>
                <div class="form-group">
                    <label>Initial Sales</label>
                    <input type="number" name="initial_sales" value="200" step="1">
                </div>
                <div class="form-group">
                    <label>Monthly Growth</label>
                    <input type="number" name="monthly_growth" value="0.05" step="0.01">
                </div>
                <div class="form-group">
                    <label>Months</label>
                    <input type="number" name="months" value="12" step="1">
                </div>
                <button type="submit">Save Scenario</button>
            </form>
        </div>
    </div>

    {'<div class="card" style="margin-top: 20px;"><h3>Load Saved Scenario</h3><form action="/scenarios/load" method="post"><div class="form-group"><select name="scenario_name" required>' + ''.join(f'<option value="{name}">{name}</option>' for name in scenario_names) + '</select></div><button type="submit">Load & Simulate</button></form></div>' if scenario_names else ''}
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/scenarios/save', methods=['POST'])
def save_scenario_post():
    scenario_name = request.form.get('scenario_name', 'untitled')
    params = {
        'fixed_costs': float(request.form.get('fixed_costs', 10000)),
        'price': float(request.form.get('price', 50)),
        'variable_cost': float(request.form.get('variable_cost', 20)),
        'initial_sales': int(request.form.get('initial_sales', 200)),
        'monthly_growth': float(request.form.get('monthly_growth', 0.05)),
        'months': int(request.form.get('months', 12)),
    }
    save_scenario(scenario_name, params)
    
    content = f'''
    <div class="alert alert-success">
        <h2>✅ Scenario Saved</h2>
        <p>Scenario <strong>"{scenario_name}"</strong> has been saved successfully!</p>
    </div>
    <div class="btn-group">
        <a href="/scenarios" class="back-link">Back to Scenarios</a>
        <a href="/" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/scenarios/load', methods=['POST'])
def load_scenario_post():
    scenario_name = request.form.get('scenario_name', '')
    try:
        params = load_scenario(scenario_name)
        
        content = f'''
        <div class="alert alert-success">
            <h2>✅ Scenario Loaded</h2>
            <p>Scenario <strong>"{scenario_name}"</strong> loaded. Click below to run simulation.</p>
        </div>
        <form action="/simulate" method="post">
            <input type="hidden" name="fixed_costs" value="{params.get('fixed_costs', 10000)}">
            <input type="hidden" name="price" value="{params.get('price', 50)}">
            <input type="hidden" name="variable_cost" value="{params.get('variable_cost', 20)}">
            <input type="hidden" name="initial_sales" value="{params.get('initial_sales', 200)}">
            <input type="hidden" name="monthly_growth" value="{params.get('monthly_growth', 0.05)}">
            <input type="hidden" name="months" value="{params.get('months', 12)}">
            <button type="submit">Run Simulation</button>
        </form>
        <div class="btn-group">
            <a href="/scenarios" class="back-link">Back</a>
        </div>
        '''
    except FileNotFoundError:
        content = f'''
        <div class="alert alert-error">
            <h2>❌ Error</h2>
            <p>Scenario <strong>"{scenario_name}"</strong> not found.</p>
        </div>
        <a href="/scenarios" class="back-link">Back</a>
        '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/scenarios/delete/<scenario_name>')
def delete_scenario_route(scenario_name):
    if delete_scenario(scenario_name):
        content = f'''
        <div class="alert alert-success">
            <h2>✅ Deleted</h2>
            <p>Scenario <strong>"{scenario_name}"</strong> has been deleted.</p>
        </div>
        <a href="/scenarios" class="back-link">Back to Scenarios</a>
        '''
    else:
        content = f'''
        <div class="alert alert-error">
            <h2>❌ Error</h2>
            <p>Scenario <strong>"{scenario_name}"</strong> not found.</p>
        </div>
        <a href="/scenarios" class="back-link">Back</a>
        '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
