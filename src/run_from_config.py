"""Run projection from a JSON config and export CSV and optional plot."""
import json
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from simulator import project_months


def load_config(path: Path):
    with path.open() as f:
        return json.load(f)


def export_csv(path: Path, results):
    with path.open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["month", "units", "revenue", "variable_costs", "profit", "cumulative_profit"])
        for r in results:
            writer.writerow([r["month"], r["units"], f"{r['revenue']:.2f}", f"{r['variable_costs']:.2f}", f"{r['profit']:.2f}", f"{r['cumulative_profit']:.2f}"])


def main():
    cfg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('sample_config.json')
    if not cfg_path.exists():
        print(f"Config not found: {cfg_path}")
        sys.exit(2)
    cfg = load_config(cfg_path)
    results = project_months(cfg['fixed_costs'], cfg['price'], cfg['variable_cost'], cfg.get('initial_sales', 100), cfg.get('monthly_growth', 0.0), cfg.get('months', 12))

    out_csv = Path(cfg.get('export_csv', 'from_config_projection.csv'))
    export_csv(out_csv, results)
    print(f"Exported CSV to {out_csv}")

    out_plot = cfg.get('export_plot')
    if out_plot:
        # call plot.py to create a PNG if matplotlib is available
        try:
            from plot import main as plot_main
            # temporary adjust argv for plot module
            import sys as _sys
            _sys_argv_backup = _sys.argv
            _sys.argv = ['plot.py', '--fixed-costs', str(cfg['fixed_costs']), '--price', str(cfg['price']), '--variable-cost', str(cfg['variable_cost']), '--initial-sales', str(cfg.get('initial_sales', 100)), '--monthly-growth', str(cfg.get('monthly_growth', 0.0)), '--months', str(cfg.get('months', 12)), '--out', out_plot]
            try:
                plot_main()
            finally:
                _sys.argv = _sys_argv_backup
            print(f"Saved plot to {out_plot}")
        except Exception as e:
            print(f"Could not create plot: {e}")


if __name__ == '__main__':
    main()
