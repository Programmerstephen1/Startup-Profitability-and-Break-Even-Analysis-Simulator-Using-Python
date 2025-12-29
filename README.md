Startup Profitability & Break-Even Analysis Simulator

A lightweight Python CLI tool to model startup economics: fixed costs, variable costs, pricing, sales growth, break-even units and timeline, and simple projections.

Run:

```bash
python src/main.py --help
```

Example:

```bash
python src/main.py --fixed-costs 10000 --price 50 --variable-cost 20 --initial-sales 200 --monthly-growth 0.05 --months 12
```

This project uses only the Python standard library so it runs without external dependencies.

Plotting (optional):

1. Install plotting dependency:

```bash
pip install -r requirements.txt
```

2. Generate a PNG projection:

```bash
python src/plot.py --fixed-costs 10000 --price 50 --variable-cost 20 --initial-sales 200 --monthly-growth 0.05 --months 12 --out projection.png
```

If `matplotlib` is not installed the script will print an install suggestion and exit.
