from flask import Flask, request, render_template_string
import json
from simulator import project_months, cohort_projection, sensitivity_analysis
from scenarios import save_scenario, load_scenario, list_scenarios, delete_scenario

app = Flask(__name__)

TABLE_ROW = "<tr><td>{month}</td><td>{units}</td><td>{revenue:.2f}</td><td>{variable_costs:.2f}</td><td>{profit:.2f}</td><td>{cumulative_profit:.2f}</td></tr>"

FORM_HTML = '''
<h1>Startup Profitability Simulator</h1>
<form action="/simulate" method="post">
  Fixed costs: <input name="fixed_costs" value="10000"><br>
  Price: <input name="price" value="50"><br>
  Variable cost: <input name="variable_cost" value="20"><br>
  Initial sales: <input name="initial_sales" value="200"><br>
  Monthly growth: <input name="monthly_growth" value="0.05"><br>
  Months: <input name="months" value="12"><br>
  <button type="submit">Run Projection</button>
</form>
<p><a href="/cohort">Cohort Projection</a> | <a href="/compare">Compare Scenarios</a> | <a href="/sensitivity">Sensitivity Analysis</a> | <a href="/scenarios">Manage Scenarios</a></p>
'''

@app.route('/')
def index():
    return render_template_string(FORM_HTML)

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
    html = f"""
    <h2>Projection Results</h2>
    <table border='1'>
      <tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable</th><th>Profit</th><th>Cumulative</th></tr>
      {rows}
    </table>
    <p><a href="/">Back</a></p>
    """
    return render_template_string(html)

@app.route('/cohort')
def cohort_form():
    html = '''
    <h2>Cohort Projection</h2>
    <form action="/cohort_simulate" method="post">
      Initial customers: <input name="initial_customers" value="100"><br>
      Monthly margin per customer: <input name="monthly_margin" value="5"><br>
      Monthly churn rate: <input name="monthly_churn" value="0.1"><br>
      Months: <input name="months" value="12"><br>
      <button type="submit">Run Cohort</button>
    </form>
    <p><a href="/">Back</a></p>
    '''
    return render_template_string(html)

@app.route('/cohort_simulate', methods=['POST'])
def cohort_simulate():
    initial = int(request.form.get('initial_customers', 100))
    monthly_margin = float(request.form.get('monthly_margin', 5.0))
    monthly_churn = float(request.form.get('monthly_churn', 0.1))
    months = int(request.form.get('months', 12))

    results = cohort_projection(initial, monthly_margin, monthly_churn, months)
    rows = ''.join(f"<tr><td>{r['month']}</td><td>{r['customers']}</td><td>{r['monthly_margin']:.2f}</td><td>{r['cumulative_margin']:.2f}</td></tr>" for r in results)
    html = f"""
    <h2>Cohort Results</h2>
    <table border='1'>
      <tr><th>Month</th><th>Customers</th><th>Monthly Margin</th><th>Cumulative</th></tr>
      {rows}
    </table>
    <p><a href="/">Back</a></p>
    """
    return render_template_string(html)

@app.route('/compare')
def compare_form():
    html = '''
    <h2>Scenario Comparison</h2>
    <form action="/compare_simulate" method="post">
      Months: <input name="months" value="12"><br>
      <button type="submit">Compare</button>
    </form>
    <p><a href="/">Back</a></p>
    '''
    return render_template_string(html)

@app.route('/compare_simulate', methods=['POST'])
def compare_simulate():
    months = int(request.form.get('months', 12))
    # Simple compare: use two different defaults
    a_results = project_months(10000, 50, 20, 200, 0.05, months)
    b_results = project_months(12000, 55, 22, 180, 0.06, months)
    rows_a = ''.join(TABLE_ROW.format(**r) for r in a_results)
    rows_b = ''.join(TABLE_ROW.format(**r) for r in b_results)
    html = f"""
    <h2>Scenario Comparison</h2>
    <h3>Scenario A</h3>
    <table border='1'>{rows_a}</table>
    <h3>Scenario B</h3>
    <table border='1'>{rows_b}</table>
    <p><a href="/">Back</a></p>
    """
    return render_template_string(html)

@app.route('/sensitivity')
def sensitivity_form():
    html = '''
    <h2>Sensitivity Analysis</h2>
    <p>Analyze how changes in key parameters affect break-even month and final profit.</p>
    <form action="/sensitivity_simulate" method="post">
      Fixed costs: <input name="fixed_costs" value="10000"><br>
      Price: <input name="price" value="50"><br>
      Variable cost: <input name="variable_cost" value="20"><br>
      Initial sales: <input name="initial_sales" value="200"><br>
      Monthly growth: <input name="monthly_growth" value="0.05"><br>
      Months: <input name="months" value="12"><br>
      Parameter to vary:
      <select name="parameter">
        <option value="price">Price</option>
        <option value="variable_cost">Variable Cost</option>
        <option value="initial_sales">Initial Sales</option>
        <option value="monthly_growth">Monthly Growth</option>
        <option value="fixed_costs">Fixed Costs</option>
      </select><br>
      Variation (e.g., 0.2 for ±20%): <input name="variation" value="0.2"><br>
      <button type="submit">Run Analysis</button>
    </form>
    <p><a href="/">Back</a></p>
    '''
    return render_template_string(html)

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
    
    rows = ''.join(f"<tr><td>{r['change_percent']:+d}%</td><td>{r['break_even_month']}</td><td>${r['final_cumulative_profit']:,.0f}</td></tr>" for r in results)
    html = f"""
    <h2>Sensitivity Analysis: {parameter}</h2>
    <table border='1'>
      <tr><th>Change</th><th>Break-Even Month</th><th>Final Profit</th></tr>
      {rows}
    </table>
    <p><a href="/sensitivity">Run Another</a> | <a href="/">Back</a></p>
    """
    return render_template_string(html)

@app.route('/scenarios')
def scenarios_list():
    scenario_names = list_scenarios()
    scenario_items = ''.join(f"<li>{name} <a href='/scenarios/delete/{name}' onclick=\"return confirm('Delete?')\">Delete</a></li>" for name in scenario_names)
    scenarios_html = f"<ul>{scenario_items}</ul>" if scenario_names else "<p>No scenarios saved yet.</p>"
    
    html = f'''
    <h2>Manage Scenarios</h2>
    <h3>Saved Scenarios</h3>
    {scenarios_html}
    <h3>Save Current Scenario</h3>
    <form action="/scenarios/save" method="post">
      Scenario name: <input name="scenario_name" value="" required><br>
      Fixed costs: <input name="fixed_costs" value="10000"><br>
      Price: <input name="price" value="50"><br>
      Variable cost: <input name="variable_cost" value="20"><br>
      Initial sales: <input name="initial_sales" value="200"><br>
      Monthly growth: <input name="monthly_growth" value="0.05"><br>
      Months: <input name="months" value="12"><br>
      <button type="submit">Save</button>
    </form>
    <h3>Load Scenario</h3>
    <form action="/scenarios/load" method="post">
      <select name="scenario_name" required>
        {' '.join(f'<option value="{name}">{name}</option>' for name in scenario_names)}
      </select>
      <button type="submit">Load</button>
    </form>
    <p><a href="/">Back</a></p>
    '''
    return render_template_string(html)

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
    html = f"""
    <h2>Scenario Saved</h2>
    <p>Scenario '{scenario_name}' saved successfully!</p>
    <p><a href="/scenarios">Back to Scenarios</a> | <a href="/">Home</a></p>
    """
    return render_template_string(html)

@app.route('/scenarios/load', methods=['POST'])
def load_scenario_post():
    scenario_name = request.form.get('scenario_name', '')
    try:
        params = load_scenario(scenario_name)
        html = f"""
        <h2>Scenario Loaded: {scenario_name}</h2>
        <p>Parameters loaded. Use the form below to simulate:</p>
        <form action="/simulate" method="post">
          <input type="hidden" name="fixed_costs" value="{params.get('fixed_costs', 10000)}">
          <input type="hidden" name="price" value="{params.get('price', 50)}">
          <input type="hidden" name="variable_cost" value="{params.get('variable_cost', 20)}">
          <input type="hidden" name="initial_sales" value="{params.get('initial_sales', 200)}">
          <input type="hidden" name="monthly_growth" value="{params.get('monthly_growth', 0.05)}">
          <input type="hidden" name="months" value="{params.get('months', 12)}">
          <button type="submit">Run Simulation</button>
        </form>
        <p><a href="/scenarios">Back</a></p>
        """
    except FileNotFoundError:
        html = f"""
        <h2>Error</h2>
        <p>Scenario '{scenario_name}' not found.</p>
        <p><a href="/scenarios">Back</a></p>
        """
    return render_template_string(html)

@app.route('/scenarios/delete/<scenario_name>')
def delete_scenario_route(scenario_name):
    if delete_scenario(scenario_name):
        html = f"""
        <h2>Deleted</h2>
        <p>Scenario '{scenario_name}' deleted.</p>
        <p><a href="/scenarios">Back</a></p>
        """
    else:
        html = f"""
        <h2>Error</h2>
        <p>Scenario '{scenario_name}' not found.</p>
        <p><a href="/scenarios">Back</a></p>
        """
    return render_template_string(html)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
