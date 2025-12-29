"""Core simulation utilities for startup profitability and break-even analysis.

Uses only standard library so it runs without extra dependencies.
"""
from typing import List, Dict


def break_even_units(fixed_costs: float, price: float, variable_cost: float) -> float:
    """Return units required to break even.

    Raises ValueError if price <= variable_cost.
    """
    margin = price - variable_cost
    if margin <= 0:
        raise ValueError("Price must be greater than variable cost per unit to reach break-even")
    return fixed_costs / margin


def project_months(fixed_costs: float, price: float, variable_cost: float, initial_sales: int,
                   monthly_growth: float, months: int) -> List[Dict]:
    """Simulate monthly revenue/costs/profit and cumulative profit.

    Returns a list of dicts with keys: month (1-based), units, revenue, costs, profit, cumulative_profit
    """
    results = []
    cumulative_profit = -fixed_costs
    units = initial_sales
    for m in range(1, months + 1):
        revenue = units * price
        variable = units * variable_cost
        profit = revenue - variable
        cumulative_profit += profit
        results.append({
            "month": m,
            "units": units,
            "revenue": revenue,
            "variable_costs": variable,
            "profit": profit,
            "cumulative_profit": cumulative_profit,
        })
        units = int(units * (1 + monthly_growth))
    return results


def break_even_month(results: List[Dict]) -> int:
    """Return the month number when cumulative_profit >= 0, or 0 if never in the provided results."""
    for r in results:
        if r["cumulative_profit"] >= 0:
            return r["month"]
    return 0


def calculate_ltv(monthly_margin_per_customer: float, monthly_churn_rate: float) -> float:
    """Estimate customer lifetime value (LTV) given monthly margin per customer and monthly churn rate.

    LTV approximation: LTV = monthly_margin / monthly_churn_rate
    Returns float('inf') if churn rate is zero.
    """
    if monthly_churn_rate <= 0:
        return float('inf')
    return monthly_margin_per_customer / monthly_churn_rate


def cac_payback_months(cac: float, monthly_margin_per_customer: float) -> int:
    """Return months to pay back Customer Acquisition Cost (CAC) given monthly margin per customer.

    Returns 0 if margin <= 0 to indicate no payback.
    """
    if monthly_margin_per_customer <= 0:
        return 0
    from math import ceil
    return int(ceil(cac / monthly_margin_per_customer))


def cohort_projection(initial_customers: int, monthly_margin_per_customer: float, monthly_churn_rate: float, months: int):
    """Return monthly cohort projection for a single acquisition cohort.

    Each month returns dict: month, customers, monthly_margin, cumulative_margin
    """
    results = []
    customers = float(initial_customers)
    cumulative = 0.0
    for m in range(1, months + 1):
        monthly_margin = customers * monthly_margin_per_customer
        cumulative += monthly_margin
        results.append({
            "month": m,
            "customers": int(customers),
            "monthly_margin": monthly_margin,
            "cumulative_margin": cumulative,
        })
        customers = customers * (1.0 - monthly_churn_rate)
    return results


