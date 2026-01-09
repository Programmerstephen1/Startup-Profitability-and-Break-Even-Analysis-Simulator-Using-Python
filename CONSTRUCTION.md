# Startup Profitability Simulator - Construction & Functionality Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Core Functionalities](#core-functionalities)
4. [Web Application Features](#web-application-features)
5. [Technical Implementation](#technical-implementation)
6. [Construction Timeline](#construction-timeline)
7. [Data Models](#data-models)
8. [Development Highlights](#development-highlights)

---

## Project Overview

**Startup Profitability & Break-Even Analysis Simulator** is a comprehensive financial modeling tool designed to help entrepreneurs and business analysts understand startup profitability dynamics, break-even points, and scenario planning.

### Purpose
The simulator enables users to:
- Model revenue and expense projections based on business parameters
- Identify break-even timing (when cumulative profit becomes positive)
- Analyze how parameter changes impact profitability (sensitivity analysis)
- Track customer cohorts and lifetime value
- Compare competing business strategies
- Save and load scenarios for future reference

### Technologies Used
- **Backend**: Python 3 with Flask web framework
- **Frontend**: HTML5, CSS3 (Logical Properties), JavaScript
- **Charting**: Chart.js with zoom/pan plugin
- **Data Format**: JSON for configuration and persistence
- **Containerization**: Docker & Docker Compose
- **API**: RESTful design with Flask blueprints

---

## Architecture

### Project Structure

```
project/
├── src/
│   ├── main.py                 # CLI interface for headless usage
│   ├── webapp.py               # Flask web application (1215 lines)
│   ├── simulator.py            # Core financial modeling engine
│   ├── scenarios.py            # Scenario persistence layer
│   ├── api.py                  # RESTful API endpoints
│   ├── plot.py                 # Data visualization utilities
│   ├── run_from_config.py      # Config-driven simulation runner
│   ├── __init__.py             # Package initialization
│   └── static/
│       └── style.css           # Professional UI styling
├── tests/
│   ├── test_simulator.py       # Unit tests for simulator
│   ├── test_webapp.py          # Web app integration tests
│   └── test_scenarios.py       # Scenario management tests
├── scenarios/                  # User-saved scenario files
├── configs/                    # Configuration templates
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Multi-container orchestration
├── requirements.txt            # Python dependencies
├── README.md                   # Quick start guide
└── CONSTRUCTION.md             # This file
```

### Design Patterns

#### 1. **Separation of Concerns**
- **simulator.py**: Pure financial calculations (no I/O)
- **webapp.py**: Web interface and HTTP routing
- **api.py**: REST endpoint definitions
- **scenarios.py**: Data persistence abstraction
- **static/style.css**: Presentation layer

#### 2. **Modular Routes**
Each major feature is its own route:
- `/simulator` - Main projection tool
- `/cohort` - Customer cohort analysis
- `/sensitivity` - Parameter sensitivity analysis
- `/compare` - Scenario comparison
- `/scenarios` - Saved scenario management

#### 3. **Template Rendering**
Uses Jinja2 templating via `render_template_string()` for dynamic HTML generation with embedded Chart.js configurations.

---

## Core Functionalities

### 1. Financial Projection Engine

**File**: `simulator.py`

#### `project_months(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months)`

Simulates monthly financial data with:
- **Revenue**: `units_sold × price`
- **Variable Costs**: `units_sold × variable_cost`
- **Monthly Profit**: `revenue - variable_costs - fixed_costs`
- **Cumulative Profit**: Running total of monthly profits
- **Units Growth**: Month-to-month exponential growth

**Output**: List of monthly dictionaries with keys:
```python
{
    'month': 1,
    'units': 200,
    'revenue': 10000,
    'variable_costs': 4000,
    'profit': -4000,
    'cumulative_profit': -4000
}
```

#### `break_even_month(results)`

Identifies the first month where cumulative profit ≥ 0.
- Returns month number or 0 if not reached within projection period
- Critical metric for startup viability assessment

#### `cohort_projection(initial_customers, profit_per_customer, growth_rate, months)`

Models customer retention and lifetime value:
- **Active Customers**: Starting cohort with monthly growth
- **Monthly Margin**: Recurring revenue per customer × active customers
- **Cumulative Margin**: Aggregated profit over time
- Simulates customer acquisition or churn scenarios

#### `sensitivity_analysis(fixed_costs, price, variable_cost, initial_sales, growth, months, vary_param, variation_range)`

Performs parameter sensitivity by:
1. Selecting a parameter to vary (price, cost, fixed costs)
2. Creating ±variation_range variations (e.g., -20%, -10%, 0%, +10%, +20%)
3. Running projection for each variation
4. Collecting break-even month and final profit for comparison

**Output**: Results showing impact of each variation on profitability

---

### 2. Web Application Routes

**File**: `webapp.py`

#### Homepage (`/`)
- **Purpose**: Persona selector and quick-start hub
- **Features**:
  - 6 business model presets (SaaS, Freemium, E-commerce, Marketplace, Consulting, Hardware)
  - Live preview of default parameters
  - Navigation to all major features
- **Tech**: JavaScript persona data binding with Jinja2

#### Main Simulator (`/simulator` + `/simulate`)
- **Purpose**: Core projection modeling interface
- **Input Fields**:
  - Fixed monthly costs (KES)
  - Price per unit (KES)
  - Variable cost per unit (KES)
  - Initial monthly sales (units)
  - Monthly growth rate (%)
  - Projection period (months)
- **Output**:
  - Break-even month highlight
  - Final cumulative profit summary
  - Monthly breakdown table
  - **Interactive Chart.js visualization** with:
    - Dual-axis display (revenue/costs vs cumulative profit)
    - Zoom/pan controls (mouse wheel + pinch)
    - Hover tooltips with KES formatting
    - PNG export button
    - CSV download button
    - Reset zoom button

#### Cohort Projection (`/cohort` + `/cohort_simulate`)
- **Purpose**: Customer retention and lifetime value analysis
- **Input Fields**:
  - Initial customers
  - Profit per customer (KES)
  - Monthly churn/growth rate (%)
  - Analysis period (months)
- **Output**:
  - Customer retention table (month, active customers, margins)
  - **Dual-axis Chart.js chart**:
    - Active customers on left axis (blue line)
    - Cumulative margin on right axis (green line)
  - Export PNG and CSV options
  - Toast notifications on export actions

#### Sensitivity Analysis (`/sensitivity` + `/sensitivity_simulate`)
- **Purpose**: Parameter impact analysis
- **Features**:
  - Select parameter to vary (Price, Variable Cost, or Fixed Costs)
  - Define variation range (%)
  - Auto-generates ±range variations
- **Output**:
  - Results table showing each variation's impact
  - **Bar chart visualization**:
    - X-axis: Parameter change percentage
    - Y-axis: Final cumulative profit (KES)
    - Color-coded bars (blue for profit)
  - Zoom/pan and export functionality
  - Identifies which parameters drive profitability most

#### Scenario Comparison (`/compare` + `/compare_simulate`)
- **Purpose**: Side-by-side strategy comparison
- **Input**: Two complete sets of business parameters
- **Output**:
  - Dual tables showing both scenarios' monthly progression
  - **Comparative line chart**:
    - Scenario A (blue line) vs Scenario B (red line)
    - X-axis: Months
    - Y-axis: Cumulative profit (KES)
    - Immediate visual comparison of profitability trajectories
  - Interactive features (zoom, pan, export)
  - Helps identify superior strategies at a glance

#### Scenario Management (`/scenarios`, `/scenarios/save`, `/scenarios/load`, `/scenarios/delete`)
- **Purpose**: Persistent configuration storage
- **Features**:
  - **Save**: Store current parameters with memorable name
  - **Load**: Retrieve saved scenario and run immediately
  - **List**: Display all saved scenarios with delete options
  - **Delete**: Remove no-longer-needed scenarios
- **Storage**: JSON files in `scenarios/` directory
- **Use Case**: A/B test multiple business models over time

---

## Web Application Features

### Interactive Charts (All Routes with Projections)

Each chart includes:

#### Zoom & Pan Controls
- **Mouse Wheel**: Zoom in/out on X-axis (timeline)
- **Click & Drag**: Pan across timeline
- **Pinch Gesture**: Zoom on touch devices
- **Reset Zoom Button**: Return to full view

#### Formatted Tooltips
- KES currency formatting with thousand separators
- Locale-aware (en-KE): "KES 12,345.67"
- Multi-dataset hover with index intersection mode
- Displays all relevant values on single hover

#### Export Functionality
- **PNG Export**: 
  - Converts chart to base64 image
  - Downloads as `chart-name.png`
  - Full resolution screenshot quality
- **CSV Download**:
  - Exports underlying data with headers
  - Proper CSV escaping for special characters
  - Suitable for Excel/Sheets import
  - Separated by month/variation

#### Toast Notifications
- Confirmation messages on export actions
- Green background with white text
- Auto-dismisses after 3 seconds
- Positioned fixed (bottom-right)
- Opacity transition for smooth fade

### Professional UI/UX

#### Responsive Design
- CSS Grid layout (`grid-2` class for 2-column on desktop, responsive on mobile)
- Flexible navigation bar with wrap
- Mobile-optimized form inputs with prefixes

#### Color Scheme
- Primary Blue (#2563eb) for main CTAs
- Success Green (#10b981) for positive metrics
- Danger Red (#ef4444) for comparisons
- Gray gradients for hierarchy

#### CSS Logical Properties
- Uses modern CSS for internationalization
- `margin-block-end` instead of `margin-bottom`
- `inset-block-end` for fixed positioning
- `inline-size` for responsive widths
- Supports future RTL layout changes

#### Form Input Masking
- KES currency prefix display
- Clean numeric-only submission
- Format on blur, allow editing on focus
- Prevents accidental text concatenation

---

## Technical Implementation

### 1. Chart.js Integration

**Library**: Chart.js 4+ with chartjs-plugin-zoom

#### Configuration Pattern
```javascript
new Chart(ctx, {
    type: 'line', // or 'bar'
    data: {
        labels: monthLabels,
        datasets: [
            {
                label: 'Revenue',
                data: revenueData,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37,99,235,0.06)',
                yAxisID: 'y'  // Dual-axis
            },
            // More datasets...
        ]
    },
    options: {
        plugins: {
            zoom: {
                pan: { enabled: true, mode: 'x' },
                zoom: { 
                    wheel: { enabled: true },
                    pinch: { enabled: true },
                    mode: 'x'
                }
            },
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const v = context.parsed.y;
                        return `${context.dataset.label}: KES ${v.toLocaleString('en-KE')}`;
                    }
                }
            }
        },
        scales: {
            y: { ticks: { callback: v => `KES ${v.toLocaleString('en-KE')}` } },
            y_margin: { position: 'right', ... }  // Dual-axis
        }
    }
});
```

### 2. Data Flow in Projections

```
User Input (HTML Form)
    ↓
POST /simulate (form data)
    ↓
simulate() function (Flask route)
    ↓
Parse & validate inputs
    ↓
project_months() (simulator.py)
    ↓
Calculate monthly results
    ↓
break_even_month() (simulator.py)
    ↓
Render Jinja2 template with:
  - HTML table (static display)
  - Chart.js config (json.dumps of results)
  - Export button handlers (JavaScript)
    ↓
Browser renders Chart.js
    ↓
User interactions (zoom, export, CSV)
```

### 3. Scenario Persistence

**File**: `scenarios.py`

#### Storage Format
```json
{
    "fixed_costs": 10000,
    "price": 50,
    "variable_cost": 20,
    "initial_sales": 200,
    "monthly_growth": 0.05,
    "months": 12
}
```

Saved as: `scenarios/{scenario_name}.json`

#### Functions
- `save_scenario(name, params)`: Write to disk
- `load_scenario(name)`: Read from disk
- `list_scenarios()`: Directory scan
- `delete_scenario(name)`: File removal

### 4. REST API Blueprint

**File**: `api.py`

Registered as Flask blueprint in `webapp.py`:
```python
app.register_blueprint(api)
```

Endpoints include:
- `GET /api/health`: Health check
- `GET /api/project`: Run projection with query params
- `GET /api/cohort`: Run cohort analysis
- `GET /api/sensitivity`: Run sensitivity analysis
- `GET /api/scenarios`: List saved scenarios
- `POST /api/scenarios`: Save new scenario
- `GET /api/scenarios/{name}`: Load scenario
- `DELETE /api/scenarios/{name}`: Delete scenario

---

## Construction Timeline

### Phase 1: Initial Development
**Goal**: Build core financial modeling engine

- Created `simulator.py` with `project_months()`, `break_even_month()`
- Implemented `cohort_projection()` for customer lifetime value
- Built `sensitivity_analysis()` for parameter impact testing
- Wrote unit tests in `test_simulator.py`

### Phase 2: CLI & API Layer
**Goal**: Enable headless usage and programmatic access

- Implemented `main.py` for command-line interface
- Created `api.py` with Flask blueprint for REST endpoints
- Added `scenarios.py` for JSON-based persistence
- Tested endpoints in `test_endpoints.py`

### Phase 3: Initial Web UI
**Goal**: Create basic web interface with forms

- Built `webapp.py` with route structure
- Implemented persona selector homepage
- Created projection form and results table
- Added scenario management interface
- Basic HTML rendering without advanced charts

### Phase 4: Chart Integration & Interactive Features
**Goal**: Add visual analysis and export capabilities

**Major enhancements:**

#### Chart.js Implementation
- Integrated Chart.js for all projection routes
- Configured dual-axis charts for multi-metric displays
- Implemented zoom/pan via chartjs-plugin-zoom
- Added tooltip callbacks for KES currency formatting

#### Cohort Charts
- Created dual-axis line chart showing:
  - Active customers (blue, left axis)
  - Cumulative margin (green, right axis)
- Pattern template reused for all subsequent routes

#### Comparison Charts
- Built side-by-side scenario comparison
- Red line for Scenario B vs Blue line for Scenario A
- X-axis: months, Y-axis: cumulative profit

#### Sensitivity Charts
- Bar chart for parameter sensitivity
- Labels show percentage change
- Color-coded by impact

#### Export Functionality
- PNG export via `chart.toBase64Image()`
- CSV generation with proper escaping
- Toast notifications for user feedback
- Consistent button styling across all routes

### Phase 5: Error Resolution & Refinement
**Goal**: Fix issues and standardize implementation

**Issues Resolved:**

1. **Duplicate Function Declarations**: ~970 lines of merged content removed
2. **Git Merge Conflicts**: All `<<<<<<< HEAD` and `>>>>>>> commit` markers removed
3. **Type Safety**: Added guards for `scenario_name` potentially being None
4. **CSS Warnings**: Converted physical properties to logical ones:
   - `bottom` → `inset-block-end`
   - `right` → `inset-inline-end`
   - `margin-bottom` → `margin-block-end`
   - `width` → `inline-size`
   - `max-height` → `max-block-size`

5. **Percent Input Normalization**: Added checks to convert percent-style inputs (e.g., "5") to decimals (0.05)

### Phase 6: Documentation & GitHub Deployment
**Goal**: Document project and push to repository

- Created comprehensive README.md
- Created this CONSTRUCTION.md guide
- All changes committed and pushed to GitHub
- Server tested and verified working on http://127.0.0.1:5000

---

## Data Models

### Projection Result Dictionary

```python
{
    'month': int,                    # Month number (1-12)
    'units': int,                    # Units sold that month
    'revenue': float,                # Revenue = units × price
    'variable_costs': float,         # Variable costs = units × var_cost
    'profit': float,                 # Monthly profit
    'cumulative_profit': float       # Running total profit
}
```

### Cohort Result Dictionary

```python
{
    'month': int,                    # Month number
    'customers': int,                # Active customers in cohort
    'monthly_margin': float,         # Revenue from this month
    'cumulative_margin': float       # Total lifetime value so far
}
```

### Sensitivity Result Dictionary

```python
{
    'change_percent': int,           # -20, -10, 0, +10, +20, etc.
    'break_even_month': int,         # When business breaks even
    'final_cumulative_profit': float # Final profit at end of period
}
```

### Scenario Configuration Dictionary

```python
{
    'fixed_costs': float,            # Monthly fixed operating costs
    'price': float,                  # Price per unit
    'variable_cost': float,          # Cost per unit produced
    'initial_sales': int,            # Starting units per month
    'monthly_growth': float,         # Growth rate (0.05 = 5%)
    'months': int                    # Projection period
}
```

---

## Development Highlights

### Key Decisions

#### 1. **JSON-based Scenario Storage**
- **Why**: Lightweight, human-readable, no database needed
- **Benefit**: Easy inspection, modification, and version control
- **Trade-off**: Not suitable for high-volume production systems

#### 2. **Chart.js with Zoom Plugin**
- **Why**: Lightweight, no dependencies, smooth interactions
- **Alternative Considered**: Plotly (heavier, but more features)
- **Benefit**: Excellent performance on modern browsers

#### 3. **Jinja2 Template Strings Over Static Files**
- **Why**: Reduces file I/O, keeps logic and presentation coupled where beneficial
- **Benefit**: Dynamic content embedding (json.dumps directly into JS)
- **Trade-off**: Less separation of concerns for very large templates

#### 4. **Logical CSS Properties**
- **Why**: Modern standard, supports RTL languages
- **Forward-Looking**: Prepares codebase for internationalization
- **Benefit**: Better long-term maintainability

### Notable Engineering Practices

#### Input Validation & Normalization
- Percent inputs (e.g., "5%") automatically converted to decimals
- Required attributes on all form inputs
- Float/int type conversion with sensible defaults

#### Error Handling
- Defensive null checks for `break_even_month` (returns "Not reached" if negative)
- Graceful CSV export escaping (quotes in data handled)
- 404 page for deleted/missing scenarios

#### Performance Optimizations
- Inline CSS and JS to reduce HTTP requests
- Chart.js datasets configured with minimal overhead
- JSON serialization once per route (not per user)

#### Accessibility Considerations
- Semantic HTML with form labels
- Color contrast ratios meet WCAG standards
- Keyboard-navigable forms
- Tooltip help text on export buttons

### Testing Strategy

**File**: `test_*.py` files

- **Unit Tests**: `test_simulator.py` for financial calculations
- **Integration Tests**: `test_webapp.py` for route behavior
- **Scenario Tests**: `test_scenarios.py` for persistence layer
- **Manual Testing**: Server started and endpoints verified (200 OK responses)

---

## Future Enhancement Opportunities

### Short-term
1. **Authentication**: Protect user scenarios with login system
2. **Multi-language Support**: Use logical CSS + i18n for internationalization
3. **Advanced Charts**: 3D visualizations, forecast confidence intervals
4. **Export Formats**: PDF reports, Excel workbooks with formulas

### Long-term
1. **Database Migration**: Move from JSON to PostgreSQL for scalability
2. **Real-time Collaboration**: WebSocket support for shared scenario editing
3. **ML Integration**: Predictive models for break-even estimation
4. **Mobile App**: React Native companion app for iOS/Android
5. **Advanced Modeling**: Seasonal variations, multiple product lines, market saturation curves

---

## Deployment Notes

### Local Development
```bash
python src/webapp.py  # Runs on localhost:5000 with debug=True
```

### Docker Deployment
```bash
docker-compose up     # Full stack with Flask app and volumes
```

### Production Considerations
- Replace `debug=True` with `debug=False`
- Use production WSGI server (Gunicorn, uWSGI)
- Set up reverse proxy (Nginx, Apache)
- Enable HTTPS/SSL
- Implement rate limiting on API
- Add proper logging and monitoring

---

## Conclusion

This project demonstrates a complete financial modeling system combining:
- **Robust Backend**: Pure Python calculations with no side effects
- **Interactive Frontend**: Modern web UI with responsive design
- **Professional Charts**: Feature-rich data visualization
- **Practical Features**: Scenario management and sensitivity analysis
- **Clean Architecture**: Modular design supporting future enhancements

The construction process emphasized correctness, user experience, and code quality at each phase. The final system provides entrepreneurs with actionable insights for startup financial planning and strategy validation.
