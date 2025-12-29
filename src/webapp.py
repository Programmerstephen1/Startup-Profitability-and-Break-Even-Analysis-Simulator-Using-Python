"""Simple Flask web UI for the Startup Profitability Simulator.

Routes:
- / : form to enter parameters
- /simulate : POST endpoint returns HTML with table and inline plot
- /plot.png : generates plot PNG for given query parameters
"""
from io import BytesIO
from pathlib import Path
from flask import Flask, request, send_file, render_template_string
import base64

ROOT = Path(__file__).resolve().parents[1]
import sys
if str(ROOT / 'src') not in sys.path:
    sys.path.insert(0, str(ROOT / 'src'))


from simulator import project_months, cohort_projection
import src.plot as plot

app = Flask(__name__)

FORM_HTML = '''
<h2>Startup Profitability Simulator</h2>
<form action="/simulate" method="post">
  Fixed costs: <input name="fixed_costs" value="10000"><br>
  Price: <input name="price" value="50"><br>
  Variable cost: <input name="variable_cost" value="20"><br>
  Initial sales: <input name="initial_sales" value="200"><br>
  Monthly growth: <input name="monthly_growth" value="0.05"><br>
  Months: <input name="months" value="12"><br>
  <button type="submit">Simulate</button>
</form>
'''

TABLE_ROW = "<tr><td>{month}</td><td>{units}</td><td>{revenue:.2f}</td><td>{variable_costs:.2f}</td><td>{profit:.2f}</td><td>{cumulative_profit:.2f}</td></tr>"


def make_plot_bytes(results):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return None
    months = [r['month'] for r in results]
    cum = [r['cumulative_profit'] for r in results]
    units = [r['units'] for r in results]
    revenue = [r['revenue'] for r in results]
    fig, ax1 = plt.subplots(figsize=(6,4))
    ax1.plot(months, cum, label='Cumulative Profit', color='green')
    ax2 = ax1.twinx()
    ax2.plot(months, units, label='Units', color='blue', linestyle='--')
    ax2.plot(months, revenue, label='Revenue', color='orange', linestyle=':')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Cumulative Profit')
    ax2.set_ylabel('Units / Revenue')
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


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
    try:
        buf = plot.make_projection_plot_bytes(results)
        img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        img_tag = f'<img src="data:image/png;base64,{img_b64}" alt="plot">'
    except Exception:
        img_tag = '<p>(plot unavailable)</p>'
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    html = f"<h2>Projection Results</h2>{img_tag}<table border='1'><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable</th><th>Profit</th><th>Cumulative</th></tr>{rows}</table>"
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
    '''
    return render_template_string(html)


@app.route('/cohort_simulate', methods=['POST'])
def cohort_simulate():
    initial = int(request.form.get('initial_customers', 100))
    monthly_margin = float(request.form.get('monthly_margin', 5.0))
    monthly_churn = float(request.form.get('monthly_churn', 0.1))
    months = int(request.form.get('months', 12))
    results = cohort_projection(initial, monthly_margin, monthly_churn, months)
    try:
        buf = plot.make_cohort_plot_bytes(results)
        img_b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        img_tag = f'<img src="data:image/png;base64,{img_b64}" alt="cohort">'
    except Exception:
        img_tag = '<p>(cohort plot unavailable)</p>'
    rows = ''.join(f"<tr><td>{r['month']}</td><td>{r['customers']}</td><td>{r['monthly_margin']:.2f}</td><td>{r['cumulative_margin']:.2f}</td></tr>" for r in results)
    html = f"<h2>Cohort Results</h2>{img_tag}<table border='1'><tr><th>Month</th><th>Customers</th><th>Monthly Margin</th><th>Cumulative</th></tr>{rows}</table>"
    return render_template_string(html)


@app.route('/compare')
def compare_form():
    html = '''
    <h2>Scenario Comparison</h2>
    <form action="/compare_simulate" method="post">
      <h3>Scenario A</h3>
      Fixed costs: <input name="a_fixed" value="10000"><br>
      Price: <input name="a_price" value="50"><br>
      Variable cost: <input name="a_var" value="20"><br>
      Initial sales: <input name="a_init" value="200"><br>
      Monthly growth: <input name="a_growth" value="0.05"><br>
      <h3>Scenario B</h3>
      Fixed costs: <input name="b_fixed" value="12000"><br>
      Price: <input name="b_price" value="55"><br>
      Variable cost: <input name="b_var" value="22"><br>
      Initial sales: <input name="b_init" value="180"><br>
      Monthly growth: <input name="b_growth" value="0.06"><br>
      Months: <input name="months" value="12"><br>
      <button type="submit">Compare</button>
    </form>
    '''
    return render_template_string(html)


@app.route('/compare_simulate', methods=['POST'])
def compare_simulate():
    months = int(request.form.get('months', 12))
    a_results = project_months(float(request.form.get('a_fixed', 10000)), float(request.form.get('a_price', 50)), float(request.form.get('a_var', 20)), int(request.form.get('a_init', 200)), float(request.form.get('a_growth', 0.05)), months)
    b_results = project_months(float(request.form.get('b_fixed', 12000)), float(request.form.get('b_price', 55)), float(request.form.get('b_var', 22)), int(request.form.get('b_init', 180)), float(request.form.get('b_growth', 0.06)), months)
    try:
        a_buf = plot.make_projection_plot_bytes(a_results)
        b_buf = plot.make_projection_plot_bytes(b_results)
        a_b64 = base64.b64encode(a_buf.getvalue()).decode('ascii')
        b_b64 = base64.b64encode(b_buf.getvalue()).decode('ascii')
        img_tag = f'<div style="display:flex;gap:10px;"><div><h4>Scenario A</h4><img src="data:image/png;base64,{a_b64}"></div><div><h4>Scenario B</h4><img src="data:image/png;base64,{b_b64}"></div></div>'
    except Exception:
        img_tag = '<p>(comparison plot unavailable)</p>'
    def rows_html(rs):
        return ''.join(TABLE_ROW.format(**r) for r in rs)
    html = f"<h2>Scenario Comparison</h2>{img_tag}<h3>Scenario A</h3><table border='1'><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable</th><th>Profit</th><th>Cumulative</th></tr>{rows_html(a_results)}</table><h3>Scenario B</h3><table border='1'><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable</th><th>Profit</th><th>Cumulative</th></tr>{rows_html(b_results)}</table>"
    return render_template_string(html)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
