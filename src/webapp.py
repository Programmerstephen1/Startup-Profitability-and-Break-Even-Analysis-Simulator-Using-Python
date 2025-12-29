from flask import Flask, request, render_template_string
import json
from simulator import project_months, cohort_projection

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
<p><a href="/cohort">Cohort Projection</a> | <a href="/compare">Compare Scenarios</a></p>
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

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
