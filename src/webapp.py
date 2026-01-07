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
        {content}
    </main>
    <footer>
        <p>&copy; 2025 Startup Simulator. Built with Python, Flask, and ❤️</p>
    </footer>
</body>
</html>
'''

TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {variable_costs:,.0f}</td><td>KES {profit:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>"


@app.route('/')
def home():
        content = '''
        <section class="card hero">
            <div class="flex" style="align-items: center; gap: 24px;">
                <div style="flex: 1;">
                    <h2 style="font-size: 36px; margin-block-end: 10px;">Startup Profitability Simulator — Plan with Confidence</h2>
                    <p class="mt-2">Pick a persona, preview defaults, and jump straight into the simulator.</p>

                    <div class="mt-3">
                        <label>Persona</label>
                        <select id="persona-select">
                            <option value="saas" title="SaaS: recurring revenue">SaaS — subscription business</option>
                            <option value="freemium" title="Freemium: many users, low conversion">Freemium — converting users</option>
                            <option value="ecommerce" title="E‑commerce: per-unit margins">E‑commerce — product margins</option>
                            <option value="marketplace" title="Marketplace: take-rate model">Marketplace — take rate model</option>
                            <option value="consulting" title="Consulting: high-ticket services">Consulting — high margin services</option>
                            <option value="hardware" title="Hardware: upfront manufacturing costs">Hardware — upfront costs</option>
                        </select>
                        <div id="persona-desc" class="mt-2 text-muted">Select a persona to see a short description and defaults.</div>

                        <div id="persona-preview" class="card mt-3" style="padding:12px;">
                            <h4 style="margin:0 0 8px 0; font-size:16px;">Preview Defaults</h4>
                            <div id="persona-defaults" class="flex"></div>
                        </div>
                    </div>
                        <script>
                            // Input masking and submit-cleaning for simulator form
                            (function(){
                                function cleanNumberString(s){ return String(s||'').replace(/[^0-9.\\-]/g,''); }
                                function formatDisplay(n){ if(n==null) return ''; const num = Number(cleanNumberString(n)); if(isNaN(num)) return ''; return 'KES ' + num.toLocaleString('en-KE'); }

                                const form = document.querySelector('form[action="/simulate"]');
                                if(!form) return;
                                // Format initial monetary inputs
                                ['fixed_costs','price','variable_cost'].forEach(name => {
                                    const el = form.querySelector('[name="'+name+'"]');
                                    if(el){ el.value = formatDisplay(el.value); el.addEventListener('focus', function(){ el.value = cleanNumberString(el.value); }); el.addEventListener('blur', function(){ el.value = formatDisplay(el.value); }); }
                                });

                                // On submit, ensure numeric-only values are sent
                                form.addEventListener('submit', function(e){
                                    ['fixed_costs','price','variable_cost'].forEach(name => {
                                        const el = form.querySelector('[name="'+name+'"]');
                                        if(el){ el.value = cleanNumberString(el.value) || '0'; }
                                    });
                                });
                            })();
                        </script>

                    <div class="mt-3">
                        <button id="start-btn">Start Simulator</button>
                        <button id="demo-btn" class="btn-secondary">Try Demo</button>
                    </div>
                </div>

                <div style="flex: 1; text-align: center;">
                    <img src="/static/hero-illustration.svg" alt="Startup illustration" style="max-inline-size: 320px; opacity: 0.95;">
                </div>
            </div>
        </section>

        <section class="grid-2 mt-4">
            <div class="card">
                 <h3>How it works</h3>
                 <p>Choose a persona to load helpful defaults, then click Start to open the simulator pre-filled for that business model.</p>
            </div>
            <div class="card">
                 <h3>Why try it</h3>
                 <p>Quickly explore pricing, margins, and growth scenarios to find robust strategies before deep-diving into projections.</p>
            </div>
        </section>

        <section class="card mt-4">
            <h3>Features</h3>
            <ul>
                <li>Quick projections: revenue, costs, and cumulative profit over time.</li>
                <li>Sensitivity analysis: understand which levers matter most.</li>
                <li>Scenario saving: compare alternate business models side-by-side.</li>
                <li>Cohort projection: model customer retention and lifetime value.</li>
            </ul>
        </section>

        <section class="card mt-4">
            <h3>Quick Start</h3>
            <ol>
                <li>Select a persona and review the preview defaults.</li>
                <li>Click <strong>Start Simulator</strong> to open the simulator pre-filled.</li>
                <li>Tweak parameters and run the projection to see break-even and cumulative profit.</li>
                <li>Save scenarios to compare different strategies.</li>
            </ol>
        </section>

        <section class="card mt-4">
            <h3>FAQ</h3>
            <p><strong>Q:</strong> Can I edit the defaults before running the simulator?<br><strong>A:</strong> Yes — the simulator form is pre-filled and fully editable.</p>
            <p><strong>Q:</strong> Are results saved?<br><strong>A:</strong> Use the Scenarios page to save and load models.</p>
        </section>

        <section class="card mt-4">
            <h3>How to Read The Graph</h3>
            <p class="text-muted">Below is an illustrative graph showing typical projection lines. Use this legend to understand projection outputs in the simulator.</p>
            <div style="display:flex; gap:20px; align-items:center;">
                <img src="/static/graph-explain.svg" alt="Graph explanation" style="max-width:320px;">
                <div>
                    <ul class="text-small">
                        <li><strong style="color:#2563eb">Revenue (blue):</strong> Monthly sales revenue.</li>
                        <li><strong style="color:#10b981">Variable Costs (green):</strong> Costs that scale with units sold.</li>
                        <li><strong style="color:#ef4444">Fixed Costs (red line):</strong> Recurring fixed operating costs.</li>
                        <li><strong style="color:#374151">Cumulative Profit (dark):</strong> Running total profit; crossing zero is break-even.</li>
                    </ul>
                </div>
            </div>
        </section>

        <script src="/static/home.js"></script>
        
        <!-- Walkthrough modal -->
        <div id="walkthrough-modal" style="display:none;">
            <div class="modal-overlay">
                <div class="modal">
                    <h3>Welcome to the Startup Profitability Simulator</h3>
                    <p>Quickly model revenue, costs, and when your business reaches break-even. Use the persona presets to get started fast or customize the defaults below before opening the simulator.</p>
                    <ul>
                        <li>Use <strong>Preview Defaults</strong> to tweak starting values on this page.</li>
                        <li>Click <strong>Start Simulator</strong> to open the full simulator pre-filled with those values.</li>
                        <li>Save scenarios to compare strategies and run sensitivity analyses to see what matters most.</li>
                    </ul>
                    <div class="actions">
                        <label style="display:flex; align-items:center; gap:8px;"><input type="checkbox" id="dont-show"> Don't show this again</label>
                        <div style="flex:1"></div>
                        <button id="walk-start" class="btn-secondary">Start Simulator</button>
                        <button id="walk-close">Close</button>
                    </div>
                </div>
            </div>
        </div>
        '''
        return render_template_string(BASE_TEMPLATE.format(content=content))


TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {variable_costs:,.0f}</td><td>KES {profit:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>"

@app.route('/simulator')
def index():
    # Allow pre-filling the simulator via GET query params (useful when coming from the homepage)
    fixed_costs = request.args.get('fixed_costs', '10000')
    price = request.args.get('price', '50')
    variable_cost = request.args.get('variable_cost', '20')
    initial_sales = request.args.get('initial_sales', '200')
    monthly_growth = request.args.get('monthly_growth', '0.05')
    months = request.args.get('months', '12')

    content = f'''
    <div class="grid-2">
        <div class="card">
            <h3>📈 Quick Projection</h3>
            <p>Model your startup's profitability over time. Enter your business parameters and see when you'll break even.</p>
            <form action="/simulate" method="post">
                <div class="form-group">
                    <label>Fixed Costs</label>
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="{fixed_costs}" step="100"></div>
                </div>
                <div class="form-group">
                    <label>Price per Unit</label>
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="{price}" step="0.01"></div>
                </div>
                <div class="form-group">
                    <label>Variable Cost per Unit</label>
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="{variable_cost}" step="0.01"></div>
                </div>
                <div class="form-group">
                    <label>Initial Sales (units)</label>
                    <input type="number" name="initial_sales" value="{initial_sales}" step="1">
                </div>
                <div class="form-group">
                    <label>Monthly Growth Rate</label>
                    <input type="number" name="monthly_growth" value="{monthly_growth}" step="0.01" min="0" max="1">
                </div>
                <div class="form-group">
                    <label>Number of Months</label>
                    <input type="number" name="months" value="{months}" step="1" min="1">
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
    
    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
    
    <div class="card">
        <h2>📊 Projection Results</h2>
        <div class="grid-2">
            <div>
                <h4>Break-Even Month</h4>
                <p style="font-size: 24px; color: var(--primary-color); font-weight: bold;">
                    {be_month}
                </p>
            </div>
            <div>
                <h4>Final Cumulative Profit</h4>
                <p style="font-size: 24px; color: var(--success-color); font-weight: bold;">
                    {final_profit}
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
    
<<<<<<< HEAD
    <div id="toast" style="position:fixed; bottom:20px; right:20px; background:#10b981; color:white; padding:12px 16px; border-radius:6px; box-shadow:0 4px 12px rgba(0,0,0,0.15); display:none; z-index:9999; opacity:0; transition:opacity 0.3s ease;"></div>

    <div class="card mt-3">
        <h3>Interactive Projection Chart</h3>
        <p class="text-muted">Zoom and hover to inspect monthly values. Double-click to reset zoom.</p>
        <div style="display:flex; gap:8px; align-items:center; margin-bottom:8px; flex-wrap:wrap;">
            <button id="export-png" class="btn-sm" title="Download chart as PNG">📥 Export PNG</button>
            <button id="download-csv" class="btn-sm btn-secondary" title="Download projection data as CSV">📊 Download CSV</button>
            <button id="reset-zoom" class="btn-sm" style="background:var(--gray-200); color:var(--gray-900);" title="Reset chart zoom">⟲ Reset Zoom</button>
            <div style="flex:1"></div>
            <small class="text-muted">Use mouse wheel or pinch to zoom, drag to pan.</small>
        </div>
        <canvas id="projection-chart" style="max-height:360px; width:100%;"></canvas>
=======
    <div class="card" style="margin-top:20px;">
        <h3>Interactive Chart</h3>
        <div id="projection-plot" style="width:100%;height:420px;"></div>
        <script>
            var plotData = {json.dumps({
                'months': [r['month'] for r in results],
                'cumulative': [r['cumulative_profit'] for r in results],
                'units': [r['units'] for r in results],
                'revenue': [r['revenue'] for r in results]
            })};
            var traceCum = {{"x": plotData.months, "y": plotData.cumulative, "name": "Cumulative Profit", "yaxis": "y1", "type": "scatter", "mode": "lines+markers", "line": {{"color": "green"}}}};
            var traceUnits = {{"x": plotData.months, "y": plotData.units, "name": "Units", "yaxis": "y2", "type": "scatter", "mode": "lines", "line": {{"color": "blue", "dash": "dash"}}}};
            var traceRevenue = {{"x": plotData.months, "y": plotData.revenue, "name": "Revenue", "yaxis": "y2", "type": "scatter", "mode": "lines", "line": {{"color": "orange", "dash": "dot"}}}};
            var data = [traceCum, traceUnits, traceRevenue];
            var layout = {{"title": "Projection Overview", "yaxis": {{"title": "Cumulative Profit", "side": "left"}}, "yaxis2": {{"title": "Units / Revenue", "overlaying": "y", "side": "right"}}}};
            Plotly.newPlot('projection-plot', data, layout, {{responsive: true}});
        </script>
>>>>>>> 9c7f0bc3d9df946df65180a17c517a99e8dcb4d4
    </div>

    <div class="btn-group">
        <a href="/simulator" class="back-link">← Dashboard</a>
        <form action="/sensitivity" method="get" style="display: inline;">
            <button type="submit" class="btn-secondary">Run Sensitivity Analysis</button>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@1.2.1/dist/chartjs-plugin-zoom.min.js"></script>
    <script>
        // Prepare chart data from projection results, enable zoom/pan and export
        (function(){
            const results = RESULTS_JSON_DATA;
            const labels = results.map(r => r.month);
            const revenue = results.map(r => Number(r.revenue));
            const variable_costs = results.map(r => Number(r.variable_costs));
            const cumulative = results.map(r => Number(r.cumulative_profit));

            const ctx = document.getElementById('projection-chart').getContext('2d');
            const projChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Revenue', data: revenue, borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,0.06)', tension: 0.2, yAxisID: 'y' },
                        { label: 'Variable Costs', data: variable_costs, borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.06)', tension: 0.2, yAxisID: 'y' },
                        { label: 'Cumulative Profit', data: cumulative, borderColor: '#374151', backgroundColor: 'rgba(55,65,81,0.04)', tension: 0.2, yAxisID: 'y_cumu' }
                    ]
                },
                options: {
                    interaction: { mode: 'index', intersect: false },
                    stacked: false,
                    plugins: {
                        zoom: {
                            pan: { enabled: true, mode: 'x' },
                            zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context){
                                    const v = context.parsed.y;
                                    return context.dataset.label + ': KES ' + Number(v).toLocaleString('en-KE');
                                }
                            }
                        }
                    },
                    scales: {
                        y: { type: 'linear', display: true, position: 'left', ticks: { callback: v => 'KES ' + Number(v).toLocaleString('en-KE') } },
                        y_cumu: { type: 'linear', display: true, position: 'right', ticks: { callback: v => 'KES ' + Number(v).toLocaleString('en-KE') } }
                    }
                }
            });

            // Toast helper
            function showToast(msg){
                const toast = document.getElementById('toast');
                toast.textContent = msg;
                toast.style.display = 'block';
                setTimeout(() => toast.style.opacity = '1', 10);
                setTimeout(() => {
                    toast.style.opacity = '0';
                    setTimeout(() => toast.style.display = 'none', 300);
                }, 3000);
            }

            // Export PNG
            const exportBtn = document.getElementById('export-png');
            if(exportBtn){
                exportBtn.addEventListener('click', function(){
                    const url = projChart.toBase64Image();
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'projection.png';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    showToast('Chart exported as PNG');
                });
            }

            // Download CSV
            const csvBtn = document.getElementById('download-csv');
            if(csvBtn){
                csvBtn.addEventListener('click', function(){
                    const rows = [['Month','Revenue','Variable Costs','Cumulative Profit']];
                    results.forEach(r => rows.push([r.month, r.revenue, r.variable_costs, r.cumulative_profit]));
                    const csv = rows.map(r => r.map(v => '"' + String(v).replace(/"/g,'""') + '"').join(',')).join('\\n');
                    const blob = new Blob([csv], {{type: 'text/csv;charset=utf-8;'}});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'projection.csv';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    URL.revokeObjectURL(url);
                    showToast('Projection data downloaded as CSV');
                });
            }

            // Reset zoom
            const resetBtn = document.getElementById('reset-zoom');
            if(resetBtn){
                resetBtn.addEventListener('click', function(){
                    projChart.resetZoom();
                });
            }
        })();
    </script>
    '''.format(
        be_month=be_month if be_month > 0 else "Not reached",
        final_profit=f"KES {final_profit:,.0f}",
        rows=rows
    )
    # Render template, embedding JSON of results for the chart
    final_content = content.replace('RESULTS_JSON_DATA', json.dumps(results))
    return render_template_string(BASE_TEMPLATE.format(content=final_content))

@app.route('/cohort')
def cohort_form():
    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
    <form action="/cohort_simulate" method="post">
        <h2>🎯 Cohort Projection</h2>
        <p class="text-muted">Analyze how a single customer cohort evolves over time with churn and lifetime value.</p>
        
        <div class="form-group">
            <label>Initial Customers</label>
            <input type="number" name="initial_customers" value="100" step="1" min="1">
        </div>
        <div class="form-group">
            <label>Monthly Margin per Customer (KES)</label>
            <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="monthly_margin" value="5" step="0.01"></div>
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
    <script>
        (function(){
            function cleanNumberString(s){ return String(s||'').replace(/[^0-9.\\-]/g,''); }
            function formatDisplay(n){ if(n==null) return ''; const num = Number(cleanNumberString(n)); if(isNaN(num)) return ''; return 'KES ' + num.toLocaleString('en-KE'); }
            const form = document.querySelector('form[action="/cohort_simulate"]');
            if(!form) return;
            const el = form.querySelector('[name="monthly_margin"]');
            if(el){
                el.value = formatDisplay(el.value);
                el.addEventListener('focus', function(){ el.value = cleanNumberString(el.value); });
                el.addEventListener('blur', function(){ el.value = formatDisplay(el.value); });
            }
            form.addEventListener('submit', function(e){
                if(el) el.value = cleanNumberString(el.value) || '0';
            });
        })();
    </script>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/cohort_simulate', methods=['POST'])
def cohort_simulate():
    initial = int(request.form.get('initial_customers', 100))
    monthly_margin = float(request.form.get('monthly_margin', 5.0))
    monthly_churn = float(request.form.get('monthly_churn', 0.1))
    months = int(request.form.get('months', 12))

    results = cohort_projection(initial, monthly_margin, monthly_churn, months)
    rows = ''.join(f"<tr><td>{r['month']}</td><td>{r['customers']:,}</td><td>KES {r['monthly_margin']:,.0f}</td><td>KES {r['cumulative_margin']:,.0f}</td></tr>" for r in results)
    
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
    
    <div class="card" style="margin-top:20px;">
        <h3>Interactive Cohort Chart</h3>
        <div id="cohort-plot" style="width:100%;height:420px;"></div>
        <script>
            var cohortData = {json.dumps({'months':[r['month'] for r in results],'customers':[r['customers'] for r in results],'cumulative':[r['cumulative_margin'] for r in results]})};
            var t1 = {{"x": cohortData.months, "y": cohortData.customers, "name": "Active Customers", "type": "scatter", "mode": "lines+markers", "line": {{"color": "blue"}}}};
            var t2 = {{"x": cohortData.months, "y": cohortData.cumulative, "name": "Cumulative Margin", "yaxis": "y2", "type": "scatter", "mode": "lines", "line": {{"color": "green", "dash":"dash"}}}};
            var data = [t1, t2];
            var layout = {{"title":"Cohort Overview","yaxis":{{"title":"Active Customers"}},"yaxis2":{{"title":"Cumulative Margin","overlaying":"y","side":"right"}}}};
            Plotly.newPlot('cohort-plot', data, layout, {{responsive: true}});
        </script>
    </div>

    <div class="btn-group">
        <a href="/cohort" class="back-link">← Back</a>
        <a href="/simulator" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/compare')
def compare_form():
    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
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
            <p><strong>Fixed Costs:</strong> KES 10,000</p>
            <p><strong>Price:</strong> KES 50</p>
            <p><strong>Variable Cost:</strong> KES 20</p>
            <p><strong>Initial Sales:</strong> 200 units</p>
            <p><strong>Growth:</strong> 5% per month</p>
        </div>
        <div class="card">
            <h3>Scenario B</h3>
            <p><strong>Fixed Costs:</strong> KES 12,000</p>
            <p><strong>Price:</strong> KES 55</p>
            <p><strong>Variable Cost:</strong> KES 22</p>
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

    <h3 style="margin-block-start: 30px;">Scenario B Results</h3>
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
    
<<<<<<< HEAD
    <div class="btn-group" style="margin-block-start: 30px;">
=======
    <div class="card" style="margin-top:20px;">
        <h3>Comparison Chart</h3>
        <div id="compare-plot" style="width:100%;height:420px;"></div>
        <script>
            var compareData = {json.dumps({'months':[r['month'] for r in a_results],'a_cum':[r['cumulative_profit'] for r in a_results],'b_cum':[r['cumulative_profit'] for r in b_results]})};
            var ta = {{"x": compareData.months, "y": compareData.a_cum, "name": "Scenario A - Cumulative", "type": "scatter", "mode": "lines+markers", "line": {{"color":"#2563eb"}}}};
            var tb = {{"x": compareData.months, "y": compareData.b_cum, "name": "Scenario B - Cumulative", "type": "scatter", "mode": "lines+markers", "line": {{"color":"#ef4444"}}}};
            Plotly.newPlot('compare-plot',[ta,tb], {{"title":"Scenario Comparison (Cumulative Profit)"}}, {{responsive:true}});
        </script>
    </div>

    <div class="btn-group" style="margin-top: 30px;">
>>>>>>> 9c7f0bc3d9df946df65180a17c517a99e8dcb4d4
        <a href="/compare" class="back-link">← Back</a>
        <a href="/simulator" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/sensitivity')
def sensitivity_form():
    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
    <form action="/sensitivity_simulate" method="post">
        <h2>🔍 Sensitivity Analysis</h2>
        <p class="text-muted">Analyze how changes in key parameters affect break-even month and final profit.</p>
        
        <h3>Business Parameters</h3>
        <div class="form-group">
            <label>Fixed Costs</label>
            <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100"></div>
        </div>
        <div class="form-group">
            <label>Price per Unit</label>
            <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="50" step="0.01"></div>
        </div>
        <div class="form-group">
            <label>Variable Cost per Unit</label>
            <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="20" step="0.01"></div>
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
    <script>
        (function(){
            function cleanNumberString(s){ return String(s||'').replace(/[^0-9.\\-]/g,''); }
            function formatDisplay(n){ if(n==null) return ''; const num = Number(cleanNumberString(n)); if(isNaN(num)) return ''; return 'KES ' + num.toLocaleString('en-KE'); }
            const form = document.querySelector('form[action="/sensitivity_simulate"]');
            if(!form) return;
            ['fixed_costs','price','variable_cost'].forEach(name => {
                const el = form.querySelector('[name="'+name+'"]');
                if(el){
                    el.value = formatDisplay(el.value);
                    el.addEventListener('focus', function(){ el.value = cleanNumberString(el.value); });
                    el.addEventListener('blur', function(){ el.value = formatDisplay(el.value); });
                }
            });
            form.addEventListener('submit', function(e){
                ['fixed_costs','price','variable_cost'].forEach(name => {
                    const el = form.querySelector('[name="'+name+'"]');
                    if(el) el.value = cleanNumberString(el.value) || '0';
                });
            });
        })();
    </script>
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
    
    rows = ''.join(f"<tr><td style='font-weight: 600;'>{r['change_percent']:+d}%</td><td>{r['break_even_month']}</td><td>KES {r['final_cumulative_profit']:,.0f}</td></tr>" for r in results)
    
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
    
    <div class="card" style="margin-top:20px;">
        <h3>Sensitivity Chart</h3>
        <div id="sensitivity-plot" style="width:100%;height:420px;"></div>
        <script>
            var sens = {json.dumps({'changes':[r['change_percent'] for r in results],'final_profit':[r['final_cumulative_profit'] for r in results]})};
            var trace = {{"x": sens.changes, "y": sens.final_profit, "type": "bar", "marker": {{"color": "#2563eb"}}}};
            var layout = {{"title": "Sensitivity: Final Profit by Parameter Change", "xaxis": {{"title": "Change (%)"}}, "yaxis": {{"title": "Final Profit"}}}};
            Plotly.newPlot('sensitivity-plot',[trace], layout, {{responsive:true}});
        </script>
    </div>

    <div class="alert alert-info">
        <strong>💡 Insight:</strong> Larger changes in break-even month and profit indicate higher sensitivity to this parameter.
    </div>
    
    <div class="btn-group">
        <a href="/sensitivity" class="back-link">Run Another</a>
        <a href="/simulator" class="back-link">Home</a>
    </div>
    '''
    return render_template_string(BASE_TEMPLATE.format(content=content))

@app.route('/scenarios')
def scenarios_list():
    scenario_names = list_scenarios()
    scenario_items = ''.join(f"<tr><td><strong>{name}</strong></td><td><a href='/scenarios/delete/{name}' class='btn-sm' onclick=\"return confirm('Delete scenario \\'{name}\\'?')\">Delete</a></td></tr>" for name in scenario_names)
    scenarios_table = f"<table><thead><tr><th>Scenario Name</th><th>Action</th></tr></thead><tbody>{scenario_items}</tbody></table>" if scenario_names else "<p class='text-muted'>No scenarios saved yet.</p>"
    
    # Build the load scenarios section
    load_scenarios_section = ''
    if scenario_names:
        options = ''.join(f'<option value="{name}">{name}</option>' for name in scenario_names)
        load_scenarios_section = f'<div class="card" style="margin-block-start: 20px;"><h3>Load Saved Scenario</h3><form action="/scenarios/load" method="post"><div class="form-group"><select name="scenario_name" required>{options}</select></div><button type="submit">Load & Simulate</button></form></div>'
    
    content = '''
    <a href="/simulator" class="back-link">← Back to Dashboard</a>
    
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
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="fixed_costs" value="10000" step="100"></div>
                </div>
                <div class="form-group">
                    <label>Price per Unit</label>
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="price" value="50" step="0.01"></div>
                </div>
                <div class="form-group">
                    <label>Variable Cost per Unit</label>
                    <div class="input-with-prefix"><span class="input-prefix">KES</span><input type="number" name="variable_cost" value="20" step="0.01"></div>
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
            <script>
                (function(){
                    function cleanNumberString(s){ return String(s||'').replace(/[^0-9.\\-]/g,''); }
                    function formatDisplay(n){ if(n==null) return ''; const num = Number(cleanNumberString(n)); if(isNaN(num)) return ''; return 'KES ' + num.toLocaleString('en-KE'); }
                    const form = document.querySelector('form[action="/scenarios/save"]');
                    if(!form) return;
                    ['fixed_costs','price','variable_cost'].forEach(name => {
                        const el = form.querySelector('[name="'+name+'"]');
                        if(el){
                            el.value = formatDisplay(el.value);
                            el.addEventListener('focus', function(){ el.value = cleanNumberString(el.value); });
                            el.addEventListener('blur', function(){ el.value = formatDisplay(el.value); });
                        }
                    });
                    form.addEventListener('submit', function(e){
                        ['fixed_costs','price','variable_cost'].forEach(name => {
                            const el = form.querySelector('[name="'+name+'"]');
                            if(el) el.value = cleanNumberString(el.value) || '0';
                        });
                    });
                })();
            </script>
        </div>
    </div>

    {load_scenarios_section}
    '''.format(
        scenarios_table=scenarios_table,
        load_scenarios_section=load_scenarios_section
    )
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
