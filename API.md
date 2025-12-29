# REST API Documentation

## Overview

The Startup Simulator provides a comprehensive REST API for programmatic access to all financial modeling features.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently no authentication required. For production deployments, add API key authentication.

## Response Format

All responses are JSON with the following format:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "error message (if status is error)"
}
```

## Endpoints

### Health Check

```http
GET /api/health
```

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "Startup Simulator API",
  "version": "1.0.0"
}
```

---

### Project Simulation

```http
GET /api/project
```

Run a projection simulation with specified parameters.

**Query Parameters:**
- `fixed_costs` (float, default: 10000): Fixed costs
- `price` (float, default: 50): Price per unit
- `variable_cost` (float, default: 20): Variable cost per unit
- `initial_sales` (int, default: 200): Initial sales/units
- `monthly_growth` (float, default: 0.05): Monthly growth rate (0-1)
- `months` (int, default: 12): Number of months to project

**Example:**
```bash
curl "http://localhost:5000/api/project?fixed_costs=10000&price=50&variable_cost=20&initial_sales=200&monthly_growth=0.05&months=12"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "month": 1,
        "units": 200,
        "revenue": 10000,
        "variable_costs": 4000,
        "profit": -4000,
        "cumulative_profit": -4000
      },
      ...
    ],
    "break_even_month": 3,
    "final_cumulative_profit": 50000
  }
}
```

---

### Cohort Projection

```http
GET /api/cohort
```

Run cohort-based customer analysis.

**Query Parameters:**
- `initial_customers` (int, default: 100): Initial customer count
- `monthly_margin` (float, default: 5.0): Monthly margin per customer
- `monthly_churn` (float, default: 0.1): Monthly churn rate (0-1)
- `months` (int, default: 12): Number of months to project

**Example:**
```bash
curl "http://localhost:5000/api/cohort?initial_customers=100&monthly_margin=5.0&monthly_churn=0.1&months=12"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "month": 1,
        "customers": 90,
        "revenue": 450,
        "cumulative_margin": 450
      },
      ...
    ],
    "final_cumulative_margin": 3000
  }
}
```

---

### Sensitivity Analysis

```http
GET /api/sensitivity
```

Analyze how parameter variations affect break-even and profit.

**Query Parameters:**
- `parameter` (string, default: "price"): Parameter to vary
  - `price`, `variable_cost`, `initial_sales`, `monthly_growth`, `fixed_costs`
- `variation` (float, default: 0.2): Variation range (e.g., 0.2 for ±20%)
- Other simulation parameters (see Project Simulation)

**Example:**
```bash
curl "http://localhost:5000/api/sensitivity?parameter=price&variation=0.2"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "parameter": "price",
    "variation_range": 0.2,
    "results": {
      "minus_20pct": {
        "break_even_month": 5,
        "final_profit": 40000
      },
      "baseline": {
        "break_even_month": 3,
        "final_profit": 50000
      },
      "plus_20pct": {
        "break_even_month": 2,
        "final_profit": 60000
      }
    }
  }
}
```

---

### List Scenarios

```http
GET /api/scenarios
```

Get list of all saved scenarios.

**Response:**
```json
{
  "status": "success",
  "data": {
    "scenarios": ["scenario1", "scenario2", "scenario3"],
    "count": 3
  }
}
```

---

### Save Scenario

```http
POST /api/scenarios
Content-Type: application/json
```

Save a new scenario with parameters.

**Request Body:**
```json
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

**Example:**
```bash
curl -X POST http://localhost:5000/api/scenarios \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_scenario",
    "fixed_costs": 10000,
    "price": 50,
    "variable_cost": 20,
    "initial_sales": 200,
    "monthly_growth": 0.05,
    "months": 12
  }'
```

**Response:**
```json
{
  "status": "success",
  "message": "Scenario \"my_scenario\" saved successfully",
  "data": {
    "name": "my_scenario"
  }
}
```

---

### Load Scenario

```http
GET /api/scenarios/{name}
```

Load a saved scenario by name.

**Example:**
```bash
curl http://localhost:5000/api/scenarios/my_scenario
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "my_scenario",
    "params": {
      "fixed_costs": 10000,
      "price": 50,
      "variable_cost": 20,
      "initial_sales": 200,
      "monthly_growth": 0.05,
      "months": 12
    }
  }
}
```

---

### Delete Scenario

```http
DELETE /api/scenarios/{name}
```

Delete a saved scenario.

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/scenarios/my_scenario
```

**Response:**
```json
{
  "status": "success",
  "message": "Scenario \"my_scenario\" deleted successfully"
}
```

---

## Error Handling

All errors return JSON with `status: "error"` and appropriate HTTP status codes:

- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Resource not found (e.g., scenario doesn't exist)
- `500 Internal Server Error`: Server error

**Example Error Response:**
```json
{
  "status": "error",
  "message": "Invalid parameter value"
}
```

---

## Usage Examples

### Python

```python
import requests

# Health check
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Run projection
params = {
    'fixed_costs': 10000,
    'price': 50,
    'variable_cost': 20,
    'initial_sales': 200,
    'monthly_growth': 0.05,
    'months': 12
}
response = requests.get('http://localhost:5000/api/project', params=params)
data = response.json()
print(f"Break-even month: {data['data']['break_even_month']}")

# Save scenario
scenario = {
    'name': 'conservative',
    'fixed_costs': 15000,
    'price': 45,
    'variable_cost': 22,
    'initial_sales': 150,
    'monthly_growth': 0.03,
    'months': 24
}
response = requests.post('http://localhost:5000/api/scenarios', json=scenario)
print(response.json())
```

### JavaScript/Node.js

```javascript
// Health check
fetch('http://localhost:5000/api/health')
  .then(r => r.json())
  .then(data => console.log(data));

// Run projection
const params = new URLSearchParams({
  fixed_costs: 10000,
  price: 50,
  variable_cost: 20,
  initial_sales: 200,
  monthly_growth: 0.05,
  months: 12
});

fetch(`http://localhost:5000/api/project?${params}`)
  .then(r => r.json())
  .then(data => {
    console.log(`Break-even month: ${data.data.break_even_month}`);
  });

// Save scenario
fetch('http://localhost:5000/api/scenarios', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'conservative',
    fixed_costs: 15000,
    price: 45,
    variable_cost: 22,
    initial_sales: 150,
    monthly_growth: 0.03,
    months: 24
  })
})
  .then(r => r.json())
  .then(data => console.log(data));
```

### cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Run projection
curl "http://localhost:5000/api/project?fixed_costs=10000&price=50&variable_cost=20&initial_sales=200&monthly_growth=0.05&months=12"

# Run sensitivity analysis
curl "http://localhost:5000/api/sensitivity?parameter=price&variation=0.2"

# List scenarios
curl http://localhost:5000/api/scenarios

# Save scenario
curl -X POST http://localhost:5000/api/scenarios \
  -H "Content-Type: application/json" \
  -d '{"name":"test","fixed_costs":10000,"price":50,"variable_cost":20,"initial_sales":200,"monthly_growth":0.05,"months":12}'
```
