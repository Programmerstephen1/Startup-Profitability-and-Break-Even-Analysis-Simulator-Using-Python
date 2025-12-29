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

from simulator import project_months

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
    plot_buf = make_plot_bytes(results)
    img_tag = ''
    if plot_buf:
        img_b64 = base64.b64encode(plot_buf.getvalue()).decode('ascii')
        img_tag = f'<img src="data:image/png;base64,{img_b64}" alt="plot">'
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    html = f"<h2>Projection Results</h2>{img_tag}<table border='1'><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable</th><th>Profit</th><th>Cumulative</th></tr>{rows}</table>"
    return render_template_string(html)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
