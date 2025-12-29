# Startup Profitability & Break-Even Analysis Simulator

A comprehensive Python tool for startup financial modeling with CLI, web UI, REST API, and Docker support.

## Quick Start

### CLI Usage

```bash
python src/main.py --help
```

Example:

```bash
python src/main.py --fixed-costs 10000 --price 50 --variable-cost 20 --initial-sales 200 --monthly-growth 0.05 --months 12
```

### Web Interface

```bash
pip install -r requirements.txt
python -m flask --app src/webapp run
```

Visit http://localhost:5000

### Docker

```bash
docker-compose up
```

Visit http://localhost:5000

## REST API

### Health Check

```bash
GET /api/health
```

### Project Simulation

```bash
GET /api/project?fixed_costs=10000&price=50&variable_cost=20&initial_sales=200&monthly_growth=0.05&months=12
```

Response:
```json
{
  "status": "success",
  "data": {
    "results": [...],
    "break_even_month": 3,
    "final_cumulative_profit": 50000
  }
}
```

### Cohort Projection

```bash
GET /api/cohort?initial_customers=100&monthly_margin=5.0&monthly_churn=0.1&months=12
```

### Sensitivity Analysis

```bash
GET /api/sensitivity?parameter=price&variation=0.2
```

Parameters: `price`, `variable_cost`, `initial_sales`, `monthly_growth`, `fixed_costs`

### Scenario Management

List scenarios:
```bash
GET /api/scenarios
```

Save scenario:
```bash
POST /api/scenarios
Content-Type: application/json

{
  "name": "my_scenario",
  "fixed_costs": 10000,
  "price": 50,
  "variable_cost": 20,
  "initial_sales": 200,
  "monthly_growth": 0.05,
  "months": 12
}
```

Load scenario:
```bash
GET /api/scenarios/{name}
```

Delete scenario:
```bash
DELETE /api/scenarios/{name}
```

## Features

- 📊 Projection modeling with growth rates
- 🎯 Break-even analysis (units and timeline)
- ⚖️ Cohort-based customer lifetime value analysis
- 🔍 Sensitivity analysis for key parameters
- 💾 Scenario save/load with JSON persistence
- 📈 Interactive web UI with charts
- 🐳 Docker containerization for easy deployment
- 🔌 REST API for programmatic access

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
python -m unittest discover -v
```

## Project Structure

```
src/
├── simulator.py      # Core financial modeling
├── main.py          # CLI interface
├── plot.py          # Plotting utilities
├── webapp.py        # Flask web app
├── api.py           # REST API endpoints
├── scenarios.py     # Scenario persistence
└── static/
    └── style.css    # UI styling

tests/
├── test_simulator.py
└── test_webapp.py
```
