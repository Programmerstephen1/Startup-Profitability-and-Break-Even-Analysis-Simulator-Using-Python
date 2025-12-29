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
    buf = make_projection_plot_bytes(results)
    out_path = Path(args.out)
    with out_path.open('wb') as f:
        f.write(buf.getvalue())
    print(f"Saved plot to {out_path}")


def make_projection_plot_bytes(results):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        raise
    months = [r["month"] for r in results]
    cum = [r["cumulative_profit"] for r in results]
    units = [r["units"] for r in results]
    revenue = [r["revenue"] for r in results]

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
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


def make_cohort_plot_bytes(cohort_results):
    try:
        import matplotlib.pyplot as plt
    except Exception:
        raise
    months = [r['month'] for r in cohort_results]
    customers = [r['customers'] for r in cohort_results]
    cum = [r['cumulative_margin'] for r in cohort_results]
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(months, customers, label='Customers', color='tab:blue', marker='o')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Active Customers', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.plot(months, cum, label='Cumulative Margin', color='tab:green', linestyle='--')
    ax2.set_ylabel('Cumulative Margin', color='tab:green')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf


if __name__ == '__main__':
    main()
