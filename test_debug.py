#!/usr/bin/env python
import sys
sys.path.insert(0, 'D:\\Project proposal\\project\\src')

from simulator import project_months, break_even_month
import json

fixed_costs = 10000
price = 50
variable_cost = 20
initial_sales = 200
monthly_growth = 0.05
months = 12

try:
    results = project_months(fixed_costs, price, variable_cost, initial_sales, monthly_growth, months)
    print(f"✓ project_months works: {len(results)} months")
    
    be_month = break_even_month(results)
    print(f"✓ break_even_month works: {be_month}")
    
    final_profit = results[-1]['cumulative_profit']
    print(f"✓ final_profit: {final_profit}")
    
    # Try to render table row
    TABLE_ROW = "<tr><td>{month}</td><td>{units:,}</td><td>KES {revenue:,.0f}</td><td>KES {variable_costs:,.0f}</td><td>KES {profit:,.0f}</td><td>KES {cumulative_profit:,.0f}</td></tr>"
    rows = ''.join(TABLE_ROW.format(**r) for r in results)
    print(f"✓ TABLE_ROW rendering works: {len(rows)} chars")
    
    # Try JSON dumps
    json_data = json.dumps(results)
    print(f"✓ json.dumps works: {len(json_data)} chars")
    
    print("\n✓ All components work!")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
