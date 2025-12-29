"""Generate and save projection plots using the simulator.

This script will prompt to install `matplotlib` if it's not available.
"""
import argparse
import sys
from pathlib import Path

from simulator import project_months


def parse_args():
    p = argparse.ArgumentParser(description="Plot startup projection charts")
    p.add_argument("--fixed-costs", type=float, required=True)
    p.add_argument("--price", type=float, required=True)
    p.add_argument("--variable-cost", type=float, required=True)
    p.add_argument("--initial-sales", type=int, default=100)
    p.add_argument("--monthly-growth", type=float, default=0.0)
    p.add_argument("--months", type=int, default=12)
    p.add_argument("--out", type=str, default="projection.png", help="Output PNG path")
    return p.parse_args()


def main():
    args = parse_args()
    results = project_months(args.fixed_costs, args.price, args.variable_cost, args.initial_sales, args.monthly_growth, args.months)
    months = [r["month"] for r in results]
    cum = [r["cumulative_profit"] for r in results]
    units = [r["units"] for r in results]
    revenue = [r["revenue"] for r in results]

    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except Exception:
        print("matplotlib is not installed. Install requirements with:\n    pip install -r requirements.txt")
        sys.exit(2)

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(months, cum, label="Cumulative Profit", color="tab:green", marker="o")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Cumulative Profit", color="tab:green")
    ax1.tick_params(axis='y', labelcolor='tab:green')

    ax2 = ax1.twinx()
    ax2.plot(months, units, label="Units", color="tab:blue", linestyle='--')
    ax2.plot(months, revenue, label="Revenue", color="tab:orange", linestyle=':')
    ax2.set_ylabel("Units / Revenue", color="tab:blue")
    ax2.tick_params(axis='y', labelcolor='tab:blue')

    fig.tight_layout()
    out_path = Path(args.out)
    fig.savefig(out_path)
    print(f"Saved plot to {out_path}")


if __name__ == '__main__':
    main()
