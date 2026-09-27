"""
Unit tests for FinancialReporter analytics, trend calculations, and charts.
"""

import unittest
from decimal import Decimal
from fintrack.models.transaction import IncomeTransaction, ExpenseTransaction
from fintrack.analytics.reporter import FinancialReporter


class TestFinancialReporter(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            IncomeTransaction(10000.0, "Salary", "2026-08-01", "Aug Salary"),
            ExpenseTransaction(2000.0, "Rent", "2026-08-02", "Aug Rent"),
            ExpenseTransaction(1000.0, "Groceries", "2026-08-05", "Aug Food"),
            IncomeTransaction(12000.0, "Salary", "2026-09-01", "Sep Salary"),
            ExpenseTransaction(2000.0, "Rent", "2026-09-02", "Sep Rent"),
            ExpenseTransaction(3000.0, "Electronics", "2026-09-10", "Monitor"),
        ]
        self.reporter = FinancialReporter(self.transactions)

    def test_overview_calculations(self):
        ov = self.reporter.calculate_overview()
        # Income: 10000 + 12000 = 22000
        # Expense: 2000 + 1000 + 2000 + 3000 = 8000
        # Net: 14000
        # Savings rate: (14000 / 22000) * 100 = 63.64%
        self.assertEqual(ov["total_income"], 22000.0)
        self.assertEqual(ov["total_expense"], 8000.0)
        self.assertEqual(ov["net_savings"], 14000.0)
        self.assertEqual(ov["savings_rate_pct"], 63.64)
        self.assertEqual(ov["transaction_count"], 6)

    def test_category_breakdown(self):
        breakdown = self.reporter.get_category_breakdown("EXPENSE")
        # Total expense = 8000
        # Rent: 4000 (50.0%)
        # Electronics: 3000 (37.5%)
        # Groceries: 1000 (12.5%)
        self.assertEqual(len(breakdown), 3)
        self.assertEqual(breakdown[0]["category"], "Rent")
        self.assertEqual(breakdown[0]["amount"], 4000.0)
        self.assertEqual(breakdown[0]["percentage"], 50.0)

    def test_monthly_trends(self):
        trends = self.reporter.get_monthly_trends()
        self.assertEqual(len(trends), 2)
        # Aug 2026
        self.assertEqual(trends[0]["period"], "2026-08")
        self.assertEqual(trends[0]["income"], 10000.0)
        self.assertEqual(trends[0]["expense"], 3000.0)
        self.assertEqual(trends[0]["net"], 7000.0)

        # Sep 2026
        self.assertEqual(trends[1]["period"], "2026-09")
        self.assertEqual(trends[1]["income"], 12000.0)
        self.assertEqual(trends[1]["expense"], 5000.0)
        self.assertEqual(trends[1]["net"], 7000.0)

    def test_ascii_bar_chart_generation(self):
        data = [("Rent", 4000.0), ("Food", 1000.0)]
        chart = self.reporter.generate_ascii_bar_chart("TEST CHART", data, max_width=20)
        self.assertIn("TEST CHART", chart)
        self.assertIn("Rent", chart)
        self.assertIn("█", chart)

    def test_full_text_report_generation(self):
        report = self.reporter.generate_full_text_report()
        self.assertIn("FINTRACK FINANCIAL REPORT STATEMENT", report)
        self.assertIn("EXECUTIVE OVERVIEW", report)
        self.assertIn("TOP EXPENSE CATEGORIES", report)


if __name__ == "__main__":
    unittest.main()
