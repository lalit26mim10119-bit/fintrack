"""
Unit tests for FinanceEngine business logic.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from decimal import Decimal
from fintrack.core.engine import FinanceEngine
from fintrack.storage.repository import JSONRepository
from fintrack.core.exceptions import RecordNotFoundError, ValidationError


class TestFinanceEngine(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test storage
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_db.json"
        self.repo = JSONRepository(str(self.db_path))
        self.engine = FinanceEngine(repository=self.repo)

    def tearDown(self):
        # Clean up temporary test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_income_and_expense(self):
        inc = self.engine.add_income(
            amount=50000.0,
            category="Salary",
            account="Bank",
            description="September Paycheck"
        )
        self.assertEqual(inc.amount, Decimal("50000.00"))

        res = self.engine.add_expense(
            amount=1500.0,
            category="Groceries",
            account="Bank",
            description="Supermarket"
        )
        exp = res["transaction"]
        self.assertEqual(exp.amount, Decimal("1500.00"))

        # Verify balance: 50000 - 1500 = 48500
        balance = self.engine.calculate_account_balance("Bank")
        self.assertEqual(balance, Decimal("48500.00"))

    def test_budget_threshold_warning(self):
        # Set budget of 2000 for Entertainment with 80% warning
        self.engine.set_budget("Entertainment", 2000.0, warning_threshold=0.80)

        # Expense of 1500 (75%) -> no warning
        res1 = self.engine.add_expense(1500.0, "Entertainment", account="Bank")
        self.assertIsNone(res1["warning"])

        # Expense of 200 (Total 1700 = 85%) -> warning triggered!
        res2 = self.engine.add_expense(200.0, "Entertainment", account="Bank")
        self.assertIsNotNone(res2["warning"])
        self.assertIn("BUDGET ALERT", res2["warning"])

        # Expense of 400 (Total 2100 > 2000) -> exceeded alert!
        res3 = self.engine.add_expense(400.0, "Entertainment", account="Bank")
        self.assertIn("BUDGET EXCEEDED", res3["warning"])

    def test_delete_transaction(self):
        inc = self.engine.add_income(1000.0, "Bonus", account="Cash")
        self.assertEqual(len(self.engine._transactions), 1)

        removed = self.engine.delete_transaction(inc.id)
        self.assertEqual(removed.id, inc.id)
        self.assertEqual(len(self.engine._transactions), 0)

        with self.assertRaises(RecordNotFoundError):
            self.engine.delete_transaction("non-existent-id")

    def test_list_and_filter_transactions(self):
        self.engine.add_income(2000.0, "Bonus", date_val="2026-09-01", account="Bank")
        self.engine.add_expense(300.0, "Dining", date_val="2026-09-05", account="Cash")
        self.engine.add_expense(400.0, "Books", date_val="2026-09-10", account="Bank", description="Python Book")

        # Filter by type
        incomes = self.engine.list_transactions(tx_type="INCOME")
        self.assertEqual(len(incomes), 1)

        # Filter by account
        cash_txs = self.engine.list_transactions(account="Cash")
        self.assertEqual(len(cash_txs), 1)
        self.assertEqual(cash_txs[0].category, "Dining")

        # Search query
        searched = self.engine.list_transactions(search_query="Python")
        self.assertEqual(len(searched), 1)
        self.assertEqual(searched[0].category, "Books")


if __name__ == "__main__":
    unittest.main()
