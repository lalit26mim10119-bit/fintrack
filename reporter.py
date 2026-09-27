"""
Financial analytics, statistics, trend calculations, and reporting engine.
Demonstrates data aggregation, mathematical computations, dictionary comprehensions,
and ASCII data visualization.
"""

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Tuple
from fintrack.models.transaction import Transaction


class FinancialReporter:
    """
    Computes summary metrics, category breakdowns, savings rates, and ASCII charts.
    """

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions

    def calculate_overview(self) -> Dict[str, Any]:
        """
        Calculates lifetime or aggregate totals: Income, Expenses, Net Savings, and Savings Rate.
        """
        total_income = Decimal("0.00")
        total_expense = Decimal("0.00")

        for tx in self.transactions:
            if tx.get_type() == "INCOME":
                total_income += tx.amount
            elif tx.get_type() == "EXPENSE":
                total_expense += tx.amount

        net_savings = total_income - total_expense
        savings_rate = (net_savings / total_income * Decimal("100.00")) if total_income > Decimal("0.00") else Decimal("0.00")

        return {
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "net_savings": float(net_savings),
            "savings_rate_pct": round(float(savings_rate), 2),
            "transaction_count": len(self.transactions)
        }

    def get_category_breakdown(self, tx_type: str = "EXPENSE") -> List[Dict[str, Any]]:
        """
        Groups transactions by category, calculates subtotals and percentage shares.
        """
        norm_type = tx_type.strip().upper()
        totals = defaultdict(Decimal)
        type_sum = Decimal("0.00")

        for tx in self.transactions:
            if tx.get_type() == norm_type:
                totals[tx.category] += tx.amount
                type_sum += tx.amount

        breakdown = []
        for cat, amt in totals.items():
            pct = (amt / type_sum * Decimal("100.00")) if type_sum > Decimal("0.00") else Decimal("0.00")
            breakdown.append({
                "category": cat,
                "amount": float(amt),
                "percentage": round(float(pct), 2)
            })

        # Sort descending by amount
        return sorted(breakdown, key=lambda item: item["amount"], reverse=True)

    def get_monthly_trends(self) -> List[Dict[str, Any]]:
        """
        Aggregates income and expenses grouped by Year-Month.
        """
        monthly = defaultdict(lambda: {"income": Decimal("0.00"), "expense": Decimal("0.00")})

        for tx in self.transactions:
            month_key = f"{tx.date.year:04d}-{tx.date.month:02d}"
            if tx.get_type() == "INCOME":
                monthly[month_key]["income"] += tx.amount
            elif tx.get_type() == "EXPENSE":
                monthly[month_key]["expense"] += tx.amount

        trends = []
        for period in sorted(monthly.keys()):
            inc = monthly[period]["income"]
            exp = monthly[period]["expense"]
            net = inc - exp
            rate = (net / inc * Decimal("100.00")) if inc > 0 else Decimal("0.00")
            trends.append({
                "period": period,
                "income": float(inc),
                "expense": float(exp),
                "net": float(net),
                "savings_rate": round(float(rate), 2)
            })

        return trends

    def generate_ascii_bar_chart(self, title: str, items: List[Tuple[str, float]], max_width: int = 30) -> str:
        """
        Renders a clean ASCII horizontal bar chart for terminal visualization.
        """
        if not items:
            return "No data available to render chart."

        max_val = max(val for _, val in items) if items else 0.0
        lines = [f"\n--- {title} ---"]

        max_label_len = min(20, max(len(label) for label, _ in items))

        for label, val in items:
            bar_len = int((val / max_val) * max_width) if max_val > 0 else 0
            bar = "█" * bar_len
            truncated_label = (label[:17] + "...") if len(label) > 20 else label
            lines.append(f"{truncated_label:<{max_label_len}} | {bar:<{max_width}} ₹{val:,.2f}")

        return "\n".join(lines)

    def generate_full_text_report(self) -> str:
        """
        Generates a comprehensive text-based financial statement report.
        """
        overview = self.calculate_overview()
        expenses_by_cat = self.get_category_breakdown("EXPENSE")
        trends = self.get_monthly_trends()

        report_lines = [
            "=" * 64,
            "               FINTRACK FINANCIAL REPORT STATEMENT               ",
            f"                  Generated On: {date.today()}                  ",
            "=" * 64,
            "",
            "1. EXECUTIVE OVERVIEW",
            f"   Total Recorded Transactions: {overview['transaction_count']}",
            f"   Total Income:               ₹{overview['total_income']:,.2f}",
            f"   Total Expenses:             ₹{overview['total_expense']:,.2f}",
            f"   Net Cashflow (Savings):     ₹{overview['net_savings']:,.2f}",
            f"   Aggregate Savings Rate:     {overview['savings_rate_pct']}%",
            "",
            "2. TOP EXPENSE CATEGORIES",
        ]

        if expenses_by_cat:
            for item in expenses_by_cat[:7]:
                report_lines.append(
                    f"   • {item['category']:<18}: ₹{item['amount']:>10,.2f} ({item['percentage']:>5.1f}%)"
                )
        else:
            report_lines.append("   No expenses recorded yet.")

        report_lines.append("")
        report_lines.append("3. MONTHLY CASHFLOW HISTORY")
        if trends:
            report_lines.append(f"   {'Period':<9} | {'Income':<12} | {'Expenses':<12} | {'Net Savings':<12}")
            report_lines.append("   " + "-" * 51)
            for t in trends:
                report_lines.append(
                    f"   {t['period']:<9} | ₹{t['income']:>10,.2f} | ₹{t['expense']:>10,.2f} | ₹{t['net']:>10,.2f}"
                )
        else:
            report_lines.append("   No monthly transactions recorded.")

        chart_data = [(c["category"], c["amount"]) for c in expenses_by_cat[:6]]
        if chart_data:
            report_lines.append(self.generate_ascii_bar_chart("EXPENSE BREAKDOWN BY CATEGORY", chart_data, max_width=25))

        report_lines.append("")
        report_lines.append("=" * 64)
        report_lines.append("                    END OF REPORT STATEMENT                     ")
        report_lines.append("=" * 64)

        return "\n".join(report_lines)
