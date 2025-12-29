"""CLI entry point for the Startup Profitability & Break-Even Simulator."""
import argparse
import csv
from pathlib import Path
import sys

# make sure relative imports work when running from project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulator import break_even_units, project_months, break_even_month


def parse_args():
    p = argparse.ArgumentParser(description="Startup profitability & break-even simulator")
    p.add_argument("--fixed-costs", type=float, required=True, help="Total fixed costs (e.g., monthly)")
    p.add_argument("--price", type=float, required=True, help="Price per unit")
    p.add_argument("--variable-cost", type=float, required=True, help="Variable cost per unit")
    p.add_argument("--initial-sales", type=int, default=100, help="Units sold in month 1")
    p.add_argument("--monthly-growth", type=float, default=0.0, help="Monthly sales growth rate (e.g., 0.05)")
    p.add_argument("--months", type=int, default=12, help="Number of months to project")
    p.add_argument("--export-csv", type=str, default="", help="Optional path to export the projection CSV")
    return p.parse_args()


def print_summary(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months, results):
    try:
        be_units = break_even_units(fixed_costs, price, variable_cost)
    except ValueError as e:
        print(f"Error calculating break-even units: {e}")
        be_units = float('inf')
    be_month = break_even_month(results)
    print("\n--- Summary ---")
    print(f"Fixed costs: {fixed_costs:.2f}")
    print(f"Price per unit: {price:.2f}")
    print(f"Variable cost per unit: {variable_cost:.2f}")
    if be_units != float('inf'):
        print(f"Break-even units (one-time sales): {be_units:.1f}")
    else:
        print("No break-even units (price <= variable cost)")
    if be_month:
        print(f"Break-even month in projection: {be_month}")
    else:
        print("No break-even within projection window")


def export_csv(path: str, results):
    path_obj = Path(path)
    with path_obj.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["month", "units", "revenue", "variable_costs", "profit", "cumulative_profit"])
        for r in results:
            writer.writerow([r["month"], r["units"], f"{r['revenue']:.2f}", f"{r['variable_costs']:.2f}", f"{r['profit']:.2f}", f"{r['cumulative_profit']:.2f}"])
    print(f"Exported projection to {path}")


def main():
    args = parse_args()
    results = project_months(args.fixed_costs, args.price, args.variable_cost, args.initial_sales,
                             args.monthly_growth, args.months)
    print_summary(args.fixed_costs, args.price, args.variable_cost, args.initial_sales, args.monthly_growth, args.months, results)
    print("\nMonth | Units | Revenue | Variable | Profit | Cumulative")
    for r in results:
        print(f"{r['month']:>3} | {r['units']:>5} | {r['revenue']:>7.2f} | {r['variable_costs']:>8.2f} | {r['profit']:>7.2f} | {r['cumulative_profit']:>10.2f}")
    if args.export_csv:
        export_csv(args.export_csv, results)


if __name__ == "__main__":
    main()
