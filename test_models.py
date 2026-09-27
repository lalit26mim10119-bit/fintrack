"""
Unit tests for domain models: Transaction, Budget, and Account.
"""

import unittest
from datetime import date
from decimal import Decimal
from fintrack.models.transaction import Transaction, IncomeTransaction, ExpenseTransaction
from fintrack.models.budget import Budget, BudgetStatus
from fintrack.models.account import Account
from fintrack.core.exceptions import ValidationError


class TestTransactionModels(unittest.TestCase):

    def test_income_transaction_creation(self):
        tx = IncomeTransaction(
            amount=5000.0,
            category="Salary",
            date_val="2026-09-01",
            description="Monthly paycheck",
            account="Bank",
            tags={"work", "primary"}
        )
        self.assertEqual(tx.get_type(), "INCOME")
        self.assertEqual(tx.amount, Decimal("5000.00"))
        self.assertEqual(tx.signed_amount(), Decimal("5000.00"))
        self.assertEqual(tx.category, "Salary")
        self.assertEqual(tx.date, date(2026, 9, 1))
        self.assertIn("work", tx.tags)

    def test_expense_transaction_creation(self):
        tx = ExpenseTransaction(
            amount="1250.75",
            category="groceries",
            description="Supermarket groceries",
            account="Cash"
        )
        self.assertEqual(tx.get_type(), "EXPENSE")
        self.assertEqual(tx.amount, Decimal("1250.75"))
        self.assertEqual(tx.signed_amount(), Decimal("-1250.75"))
        self.assertEqual(tx.category, "Groceries")  # Auto title-cased

    def test_negative_or_zero_amount_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            IncomeTransaction(amount=0.0, category="Bonus")

        with self.assertRaises(ValidationError):
            ExpenseTransaction(amount="-50.00", category="Snacks")

    def test_invalid_date_format_raises_validation_error(self):
        with self.assertRaises(ValidationError):
            ExpenseTransaction(amount=100.0, category="Books", date_val="invalid-date-format")

    def test_serialization_roundtrip(self):
        tx = ExpenseTransaction(
            amount=250.0,
            category="Coffee",
            date_val="2026-09-15",
            description="Latte and snack",
            account="Cash",
            tags=["beverage", "quick"]
        )
        tx_dict = tx.to_dict()
        reconstructed = Transaction.from_dict(tx_dict)
        self.assertEqual(tx.id, reconstructed.id)
        self.assertEqual(tx.amount, reconstructed.amount)
        self.assertEqual(tx.get_type(), reconstructed.get_type())
        self.assertEqual(tx.tags, reconstructed.tags)


class TestBudgetModel(unittest.TestCase):

    def test_budget_evaluation_healthy(self):
        budget = Budget(category="Dining", limit_amount=5000.0, warning_threshold=0.80)
        eval_res = budget.evaluate(Decimal("2500.00"))
        self.assertEqual(eval_res["status"], BudgetStatus.HEALTHY)
        self.assertEqual(eval_res["percentage"], 50.0)
        self.assertEqual(eval_res["remaining"], 2500.0)

    def test_budget_evaluation_warning(self):
        budget = Budget(category="Dining", limit_amount=5000.0, warning_threshold=0.80)
        eval_res = budget.evaluate(Decimal("4200.00"))
        self.assertEqual(eval_res["status"], BudgetStatus.WARNING)
        self.assertEqual(eval_res["percentage"], 84.0)

    def test_budget_evaluation_exceeded(self):
        budget = Budget(category="Dining", limit_amount=5000.0, warning_threshold=0.80)
        eval_res = budget.evaluate(Decimal("5200.00"))
        self.assertEqual(eval_res["status"], BudgetStatus.EXCEEDED)
        self.assertTrue(eval_res["is_over"])


class TestAccountModel(unittest.TestCase):

    def test_account_creation_and_attributes(self):
        acc = Account("Emergency Fund", "SAVINGS", initial_balance="10000.00")
        self.assertEqual(acc.name, "Emergency Fund")
        self.assertEqual(acc.account_type, "SAVINGS")
        self.assertEqual(acc.initial_balance, Decimal("10000.00"))


if __name__ == "__main__":
    unittest.main()
