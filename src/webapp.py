"""
Canonical single webapp for the project. This file is generated to replace the messy/duplicated `src/webapp.py`.
It is based on the clean rewrite but includes a few defensive fixes:
- Normalize percent inputs (monthly growth and variation ranges)
- Fix argument order for `cohort_projection`
- Call `sensitivity_analysis` with full argument list
- Avoid concatenating None values when loading scenarios
"""
from flask import Flask, request, render_template_string
import json
from simulator import project_months, cohort_projection, sensitivity_analysis, break_even_month
from scenarios import save_scenario, load_scenario, list_scenarios, delete_scenario
from api import api

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.register_blueprint(api)

BASE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Profitability Simulator</title>
    <link rel="stylesheet" href="/static/style.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <header>
        <div class="container">
            <h1>📊 Startup Profitability Simulator</h1>
            <p>Analyze financial projections, break-even points, and business scenarios</p>
            <nav>
                <a href="/">Home</a>
                <a href="/simulator">Simulator</a>
                <a href="/sensitivity">Sensitivity Analysis</a>
                <a href="/cohort">Cohort Projection</a>
                <a href="/compare">Compare Scenarios</a>
                <a href="/scenarios">Manage Scenarios</a>
            </nav>
        </div>
    </header>
    <main class="container">
        {{ content_html|safe }}
    </main>
    <footer>
        <p>&copy; 2025 Startup Simulator. Built with Python, Flask, and ❤️</p>
    </footer>
</body>
</html>'''

TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {variable_costs:,.0f}</td><td>KES {profit:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>"


def build_persona_presets():
    return {
        'saas': {'desc': 'Recurring subscription revenue model', 'fixed_costs': 8000, 'price': 100, 'variable_cost': 10, 'initial_sales': 50, 'monthly_growth': 0.08},
        'freemium': {'desc': 'High user volume, low conversion rate', 'fixed_costs': 5000, 'price': 50, 'variable_cost': 5, 'initial_sales': 500, 'monthly_growth': 0.05},
        'ecommerce': {'desc': 'Product-based e-commerce with per-unit margins', 'fixed_costs': 12000, 'price': 75, 'variable_cost': 30, 'initial_sales': 200, 'monthly_growth': 0.06},
        'marketplace': {'desc': 'Take-rate model on transaction volume', 'fixed_costs': 10000, 'price': 100, 'variable_cost': 20, 'initial_sales': 150, 'monthly_growth': 0.1},
        'consulting': {'desc': 'High-ticket services with variable delivery costs', 'fixed_costs': 3000, 'price': 500, 'variable_cost': 150, 'initial_sales': 20, 'monthly_growth': 0.04},
        'hardware': {'desc': 'Upfront manufacturing, supply chain costs', 'fixed_costs': 20000, 'price': 200, 'variable_cost': 80, 'initial_sales': 100, 'monthly_growth': 0.03}
    }


@app.route('/')
def home():
    personas = build_persona_presets()
    persona_html = '''
    <section class="card hero">
        <div class="flex" style="align-items: center; gap: 24px;">
            <div style="flex: 1;">
                <h2 style="font-size: 36px; margin-block-end: 10px;">Startup Profitability Simulator — Plan with Confidence</h2>
                <p class="mt-2">Pick a persona, preview defaults, and jump straight into the simulator.</p>

                <div class="mt-3">
                    <label>Persona</label>
                    <select id="persona-select">
                        <option value="saas">SaaS — subscription business</option>
                        <option value="freemium">Freemium — converting users</option>
                        <option value="ecommerce">E‑commerce — product margins</option>
                        <option value="marketplace">Marketplace — take rate model</option>
                        <option value="consulting">Consulting — high margin services</option>
                        <option value="hardware">Hardware — upfront costs</option>
                    </select>
                    <div id="persona-desc" class="mt-2 text-muted">Select a persona to see a short description and defaults.</div>

                    <div id="persona-preview" class="card mt-3" style="padding:12px;">
                        <h4 style="margin:0 0 8px 0; font-size:16px;">Preview Defaults</h4>
                        <div id="persona-defaults" class="flex"></div>
                    </div>
                </div>

                <div class="mt-3"><form action="/simulator" method="get" style="display:flex;"><button type="submit" class="btn">→ Go to Simulator</button></form></div>
            </div>
        </div>
    </section>

    <script>
        var personas = ''' + json.dumps(personas) + ''';
        var selectEl = document.getElementById('persona-select');
        var descEl = document.getElementById('persona-desc');
        var defaultsEl = document.getElementById('persona-defaults');
        function updatePersona(){var key=selectEl.value; var p=personas[key]; descEl.textContent=p.desc; var html=''; html+='<div style="flex:1"><label>Fixed Costs</label><input type="number" value="'+p.fixed_costs+'" readonly></div>'; html+='<div style="flex:1"><label>Price</label><input type="number" value="'+p.price+'" readonly></div>'; html+='<div style="flex:1"><label>Variable Cost</label><input type="number" value="'+p.variable_cost+'" readonly></div>'; defaultsEl.innerHTML=html;} selectEl.addEventListener('change', updatePersona); updatePersona();
    </script>
    '''
    return render_template_string(BASE_TEMPLATE, content_html=persona_html)


@app.route('/simulator')
def simulator_form():
    content = '''
    <a href="/" class="back-link">← Back to Home</a>
    <div class="card">
        <h2>📊 Create Your Projection</h2>
        <form action="/simulate" method="post">
            <div class="grid-2">
                <div>
                    <h4>Financial Parameters</h4>
                    <div class="form-group"><label>Fixed Costs (monthly)</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100" required></div></div>
                    <div class="form-group"><label>Price per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="50" step="0.01" required></div></div>
                    <div class="form-group"><label>Variable Cost per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="20" step="0.01" required></div></div>
                </div>
                <div>
                    <h4>Growth & Timeline</h4>
                    <div class="form-group"><label>Initial Monthly Sales</label><input type="number" name="initial_sales" value="200" step="1" required></div>
                    <div class="form-group"><label>Monthly Growth Rate (%)</label><input type="number" name="monthly_growth" value="5" step="0.1" required></div>
                    <div class="form-group"><label>Projection Months</label><input type="number" name="months" value="12" step="1" required></div>
                </div>
            </div>
            <button type="submit" class="btn">Run Simulation</button>
        </form>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/simulate', methods=['POST'])
def simulate():
    fixed_costs = float(request.form.get('fixed_costs', 10000))
    price = float(request.form.get('price', 50))
    variable_cost = float(request.form.get('variable_cost', 20))
    initial_sales = int(request.form.get('initial_sales', 200))
    monthly_growth = float(request.form.get('monthly_growth', 0.05))
    if monthly_growth > 1:
        monthly_growth = monthly_growth / 100.0
    months = int(request.form.get('months', 12))

    results = project_months(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months)
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    be_month = break_even_month(results)
    final_profit = results[-1]['cumulative_profit'] if results else 0
    results_json = json.dumps(results)

    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
    <div class="card">
        <h2>📊 Projection Results</h2>
        <div class="grid-2">
            <div><h4>Break-Even Month</h4><p>''' + (str(be_month) if be_month > 0 else "Not reached") + '''</p></div>
            <div><h4>Final Cumulative Profit</h4><p>KES ''' + f'{final_profit:,.0f}' + '''</p></div>
        </div>
    </div>

    <table>
        <thead><tr><th>Month</th><th>Units Sold</th><th>Revenue</th><th>Variable Costs</th><th>Monthly Profit</th><th>Cumulative Profit</th></tr></thead>
        <tbody>''' + rows + '''</tbody>
    </table>

    <div class="card mt-3">
        <h3>Interactive Projection Chart</h3>
        <canvas id="projection-chart" style="max-height:360px; width:100%;"></canvas>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.2.1/dist/chartjs-plugin-zoom.min.js"></script>
    <script>
        var resultsData = ''' + results_json + ''';
        var labels = resultsData.map(function(r){ return r.month; });
        var revenue = resultsData.map(function(r){ return Number(r.revenue); });
        var variable_costs = resultsData.map(function(r){ return Number(r.variable_costs); });
        var cumulative = resultsData.map(function(r){ return Number(r.cumulative_profit); });
        var ctx = document.getElementById('projection-chart').getContext('2d');
        var projChart = new Chart(ctx, {
            type: 'line',
            data: { labels: labels, datasets: [{ label: 'Revenue', data: revenue, borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.06)', tension: 0.2, yAxisID: 'y' }, { label: 'Variable Costs', data: variable_costs, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.06)', tension: 0.2, yAxisID: 'y' }, { label: 'Cumulative Profit', data: cumulative, borderColor: '#374151', backgroundColor: 'rgba(55,65,81,0.04)', tension: 0.2, yAxisID: 'y_cumu' }] },
            options: { interaction: { mode: 'index', intersect: false }, plugins: { zoom: { pan: { enabled: true, mode: 'x' }, zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' } } } }
        });
    </script>

    '''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/cohort')
def cohort_form():
    content = '''
    <a href="/" class="back-link">← Back to Home</a>
    <div class="card">
        <h2>👥 Cohort Projection Analysis</h2>
        <form action="/cohort_simulate" method="post">
            <div class="grid-2">
                <div>
                    <div class="form-group"><label>Fixed Costs (monthly)</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100" required></div></div>
                    <div class="form-group"><label>Profit per Customer</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="profit_per_customer" value="50" step="0.01" required></div></div>
                    <div class="form-group"><label>Initial Customers</label><input type="number" name="initial_customers" value="100" step="1" required></div>
                </div>
                <div>
                    <div class="form-group"><label>Months to Analyze</label><input type="number" name="months" value="12" step="1" required></div>
                    <div class="form-group"><label>Monthly Churn Rate (%)</label><input type="number" name="growth_rate" value="5" step="0.1" required></div>
                </div>
            </div>
            <button type="submit" class="btn">Analyze Cohorts</button>
        </form>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/cohort_simulate', methods=['POST'])
def cohort_simulate():
    fixed_costs = float(request.form.get('fixed_costs', 10000))
    profit_per_customer = float(request.form.get('profit_per_customer', 50))
    initial_customers = int(request.form.get('initial_customers', 100))
    months = int(request.form.get('months', 12))
    growth_rate = float(request.form.get('growth_rate', 0.05))
    if growth_rate > 1:
        growth_rate = growth_rate / 100.0

    results = cohort_projection(initial_customers, profit_per_customer, growth_rate, months)
    rows = ''.join('<tr><td>{month}</td><td>{customers:,}</td><td>KES {monthly_margin:,.0f}</td><td>KES {cumulative_margin:,.0f}</td></tr>'.format(**r) for r in results)

    content = '''
    <a href="/cohort" class="back-link">← Back</a>
    <div class="card"><h2>👥 Cohort Analysis Results</h2><table><thead><tr><th>Month</th><th>Customers</th><th>Monthly Margin</th><th>Cumulative Margin</th></tr></thead><tbody>''' + rows + '''</tbody></table></div>
    <div class="btn-group"><a href="/cohort" class="back-link">Run Another</a><a href="/" class="back-link">Home</a></div>
    '''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/compare')
def compare_form():
    content = '''
    <a href="/" class="back-link">← Back to Home</a>
    <div class="card"><h2>🔄 Compare Two Scenarios</h2><form action="/compare_simulate" method="post"><div class="grid-2"><div><h4>Scenario A</h4><div class="form-group"><label>Fixed Costs</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="a_fixed_costs" value="10000" step="100" required></div></div><div class="form-group"><label>Price per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="a_price" value="50" step="0.01" required></div></div><div class="form-group"><label>Variable Cost</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="a_variable_cost" value="20" step="0.01" required></div></div></div><div><h4>Scenario B</h4><div class="form-group"><label>Fixed Costs</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="b_fixed_costs" value="15000" step="100" required></div></div><div class="form-group"><label>Price per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="b_price" value="75" step="0.01" required></div></div><div class="form-group"><label>Variable Cost</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="b_variable_cost" value="25" step="0.01" required></div></div></div></div><button type="submit" class="btn">Compare</button></form></div>
    '''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/compare_simulate', methods=['POST'])
def compare_simulate():
    a_fixed = float(request.form.get('a_fixed_costs', 10000))
    a_price = float(request.form.get('a_price', 50))
    a_var_cost = float(request.form.get('a_variable_cost', 20))
    b_fixed = float(request.form.get('b_fixed_costs', 15000))
    b_price = float(request.form.get('b_price', 75))
    b_var_cost = float(request.form.get('b_variable_cost', 25))
    months = 12
    initial_sales = 200
    growth = 0.05
    results_a = project_months(a_fixed, a_price, a_var_cost, initial_sales, growth, months)
    results_b = project_months(b_fixed, b_price, b_var_cost, initial_sales, growth, months)
    rows_a = ''.join('<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>'.format(**r) for r in results_a)
    rows_b = ''.join('<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>'.format(**r) for r in results_b)
    content = '''<a href="/compare" class="back-link">← Back</a><div class="grid-2"><div class="card"><h3>Scenario A</h3><table><thead><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Cumulative Profit</th></tr></thead><tbody>''' + rows_a + '''</tbody></table></div><div class="card"><h3>Scenario B</h3><table><thead><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Cumulative Profit</th></tr></thead><tbody>''' + rows_b + '''</tbody></table></div></div><div class="btn-group"><a href="/compare" class="back-link">Compare Again</a><a href="/" class="back-link">Home</a></div>'''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/sensitivity')
def sensitivity_form():
    content = '''
    <a href="/" class="back-link">← Back to Home</a>
    <div class="card"><h2>📈 Sensitivity Analysis</h2><form action="/sensitivity_simulate" method="post"><div class="grid-2"><div><div class="form-group"><label>Base Fixed Costs</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100" required></div></div><div class="form-group"><label>Base Price</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="50" step="0.01" required></div></div><div class="form-group"><label>Base Variable Cost</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="20" step="0.01" required></div></div></div><div><div class="form-group"><label>Parameter to Vary</label><select name="vary_param" required><option value="price">Price</option><option value="variable_cost">Variable Cost</option><option value="fixed_costs">Fixed Costs</option></select></div><div class="form-group"><label>Variation Range (%)</label><input type="number" name="variation_range" value="20" step="1" required></div></div></div><button type="submit" class="btn">Run Analysis</button></form></div>'''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/sensitivity_simulate', methods=['POST'])
def sensitivity_simulate():
    fixed_costs = float(request.form.get('fixed_costs', 10000))
    price = float(request.form.get('price', 50))
    variable_cost = float(request.form.get('variable_cost', 20))
    vary_param = request.form.get('vary_param', 'price')
    variation_range = float(request.form.get('variation_range', 20))
    if variation_range > 1:
        variation_range = variation_range / 100.0
    initial_sales = int(request.form.get('initial_sales', 200))
    monthly_growth = float(request.form.get('monthly_growth', 0.05))
    if monthly_growth > 1:
        monthly_growth = monthly_growth / 100.0
    months = int(request.form.get('months', 12))
    results = sensitivity_analysis(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months, vary_param, variation_range)
    rows = ''.join('<tr><td>{change_percent}%</td><td>{break_even_month}</td><td>KES {final_cumulative_profit:,.0f}</td></tr>'.format(**r) for r in results)
    content = '''<a href="/sensitivity" class="back-link">← Back</a><div class="card"><h2>📈 Sensitivity Results</h2><p>How ''' + vary_param + ''' changes affect profitability:</p><table><thead><tr><th>''' + vary_param.replace('_',' ').title() + '''</th><th>Break-Even Month</th><th>Final Profit</th></tr></thead><tbody>''' + rows + '''</tbody></table></div><div class="btn-group"><a href="/sensitivity" class="back-link">Run Another</a><a href="/" class="back-link">Home</a></div>'''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/scenarios')
def scenarios_list():
    scenario_names = list_scenarios()
    if scenario_names:
        rows = ''.join('<tr><td><strong>{0}</strong></td><td><a href="/scenarios/delete/{0}" class="btn-sm" onclick="return confirm(\'Delete {0}?\')">Delete</a></td></tr>'.format(name) for name in scenario_names)
        scenarios_table = '<table><thead><tr><th>Scenario Name</th><th>Action</th></tr></thead><tbody>' + rows + '</tbody></table>'
    else:
        scenarios_table = '<p class="text-muted">No scenarios saved yet.</p>'
    if scenario_names:
        options = ''.join('<option value="{0}">{0}</option>'.format(name) for name in scenario_names)
        load_section = '<div class="card" style="margin-block-start: 20px;"><h3>Load Saved Scenario</h3><form action="/scenarios/load" method="post"><div class="form-group"><select name="scenario_name" required>' + options + '</select></div><button type="submit">Load</button></form></div>'
    else:
        load_section = ''
    content = '''<a href="/" class="back-link">← Back to Home</a><h2>💾 Manage Scenarios</h2><p>Save and load your simulation configurations.</p><div class="grid-2"><div class="card"><h3>Saved Scenarios</h3>''' + scenarios_table + '''</div><div class="card"><h3>Save New Scenario</h3><form action="/scenarios/save" method="post"><div class="form-group"><label>Scenario Name</label><input type="text" name="scenario_name" placeholder="e.g., Conservative Plan" required></div><div class="form-group"><label>Fixed Costs</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100"></div></div><div class="form-group"><label>Price per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="50" step="0.01"></div></div><div class="form-group"><label>Variable Cost per Unit</label><div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="20" step="0.01"></div></div><div class="form-group"><label>Initial Sales</label><input type="number" name="initial_sales" value="200" step="1"></div><div class="form-group"><label>Monthly Growth (%)</label><input type="number" name="monthly_growth" value="5" step="0.1"></div><div class="form-group"><label>Months</label><input type="number" name="months" value="12" step="1"></div><button type="submit">Save Scenario</button></form></div></div>''' + load_section + ''''''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/scenarios/save', methods=['POST'])
def save_scenario_post():
    name = request.form.get('scenario_name', 'Unnamed')
    params = {
        'fixed_costs': float(request.form.get('fixed_costs', 10000)),
        'price': float(request.form.get('price', 50)),
        'variable_cost': float(request.form.get('variable_cost', 20)),
        'initial_sales': int(request.form.get('initial_sales', 200)),
        'monthly_growth': float(request.form.get('monthly_growth', 0.05)),
        'months': int(request.form.get('months', 12))
    }
    save_scenario(name, params)
    return '<script>alert("Scenario saved!"); window.location="/scenarios";</script>'


@app.route('/scenarios/load', methods=['POST'])
def load_scenario_post():
    name = request.form.get('scenario_name')
    if not name:
        return '<script>alert("No scenario specified"); window.location="/scenarios";</script>'
    scenario = load_scenario(name)
    if not scenario:
        return '<script>alert("Scenario not found!"); window.location="/scenarios";</script>'
    p = scenario
    results = project_months(p['fixed_costs'], p['price'], p['variable_cost'], p['initial_sales'], p['monthly_growth'], p['months'])
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    be_month = break_even_month(results)
    final_profit = results[-1]['cumulative_profit'] if results else 0
    content = '''<a href="/scenarios" class="back-link">← Back to Scenarios</a><div class="card"><h2>Loaded: ''' + name + '''</h2><div class="grid-2"><div><h4>Break-Even Month</h4><p>''' + (str(be_month) if be_month > 0 else "Not reached") + '''</p></div><div><h4>Final Profit</h4><p>KES ''' + f'{final_profit:,.0f}' + '''</p></div></div></div><table><thead><tr><th>Month</th><th>Units</th><th>Revenue</th><th>Variable Costs</th><th>Monthly Profit</th><th>Cumulative Profit</th></tr></thead><tbody>''' + rows + '''</tbody></table>'''
    return render_template_string(BASE_TEMPLATE, content_html=content)


@app.route('/scenarios/delete/<scenario_name>')
def delete_scenario_route(scenario_name):
    delete_scenario(scenario_name)
    return '<script>alert("Scenario deleted!"); window.location="/scenarios";</script>'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
