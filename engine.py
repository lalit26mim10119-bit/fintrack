"""
Core business logic engine for FinTrack.
Serves as the central domain orchestrator (Facade pattern) coordinating transactions,
accounts, budgets, validation, and persistent storage.
"""

from datetime import date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Set
from fintrack.models.transaction import Transaction, IncomeTransaction, ExpenseTransaction
from fintrack.models.budget import Budget, BudgetStatus
from fintrack.models.account import Account
from fintrack.core.exceptions import (
    RecordNotFoundError,
    ValidationError,
    InsufficientBalanceError,
    BudgetExceededError
)
from fintrack.core.validator import Validator
from fintrack.storage.repository import DataRepository, JSONRepository
from fintrack.storage.csv_handler import CSVHandler


class FinanceEngine:
    """
    Central operational engine managing financial entities and workflows.
    """

    def __init__(self, repository: DataRepository = None):
        self.repository = repository or JSONRepository()
        self._transactions: Dict[str, Transaction] = {}
        self._accounts: Dict[str, Account] = {}
        self._budgets: Dict[str, Budget] = {}
        self.load_from_storage()

    def load_from_storage(self) -> None:
        """Loads domain models from the underlying storage repository."""
        data = self.repository.load_data()

        # Load Accounts
        self._accounts.clear()
        for raw_acc in data.get("accounts", []):
            try:
                acc = Account.from_dict(raw_acc)
                self._accounts[acc.name.lower()] = acc
            except Exception:
                continue

        # Ensure default accounts exist
        if "bank" not in self._accounts:
            self._accounts["bank"] = Account("Bank", "CHECKING")
        if "cash" not in self._accounts:
            self._accounts["cash"] = Account("Cash", "CASH")

        # Load Budgets
        self._budgets.clear()
        for raw_b in data.get("budgets", []):
            try:
                b = Budget.from_dict(raw_b)
                self._budgets[b.category.lower()] = b
            except Exception:
                continue

        # Load Transactions
        self._transactions.clear()
        for raw_tx in data.get("transactions", []):
            try:
                tx = Transaction.from_dict(raw_tx)
                self._transactions[tx.id] = tx
            except Exception:
                continue

    def save_to_storage(self) -> None:
        """Serializes current in-memory domain state to storage."""
        data = {
            "version": "1.0",
            "accounts": [acc.to_dict() for acc in self._accounts.values()],
            "budgets": [b.to_dict() for b in self._budgets.values()],
            "transactions": [tx.to_dict() for tx in sorted(self._transactions.values(), key=lambda x: x.date, reverse=True)]
        }
        self.repository.save_data(data)

    # ---------------------------------------------------------
    # Transaction Management
    # ---------------------------------------------------------

    def add_income(
        self,
        amount: Any,
        category: str,
        date_val: Any = None,
        description: str = "Income",
        account: str = "Bank",
        tags: Any = None
    ) -> IncomeTransaction:
        """Creates, validates, records and saves an income transaction."""
        tx = IncomeTransaction(
            amount=amount,
            category=category,
            date_val=date_val,
            description=description,
            account=account,
            tags=tags
        )
        self._transactions[tx.id] = tx
        self.save_to_storage()
        return tx

    def add_expense(
        self,
        amount: Any,
        category: str,
        date_val: Any = None,
        description: str = "Expense",
        account: str = "Bank",
        tags: Any = None,
        enforce_budget: bool = False
    ) -> Dict[str, Any]:
        """
        Creates, validates, records and saves an expense transaction.
        Optionally evaluates budget impact and warnings.
        """
        tx = ExpenseTransaction(
            amount=amount,
            category=category,
            date_val=date_val,
            description=description,
            account=account,
            tags=tags
        )

        budget_warning = None
        # Check budget alert if budget exists for this category
        b_key = tx.category.lower()
        if b_key in self._budgets:
            budget = self._budgets[b_key]
            # Calculate current month's spending including this new expense
            current_month_spent = self.get_category_spending(
                category=tx.category,
                month=tx.date.month,
                year=tx.date.year
            ) + tx.amount

            evaluation = budget.evaluate(current_month_spent)
            if evaluation["status"] == BudgetStatus.EXCEEDED:
                budget_warning = (
                    f"BUDGET EXCEEDED: Category '{tx.category}' limit is ₹{budget.limit_amount:.2f}. "
                    f"Current spending will reach ₹{current_month_spent:.2f} ({evaluation['percentage']}%)."
                )
                if enforce_budget:
                    raise BudgetExceededError(budget_warning, category=tx.category, limit=float(budget.limit_amount), spent=float(current_month_spent))
            elif evaluation["status"] == BudgetStatus.WARNING:
                budget_warning = (
                    f"BUDGET ALERT: Category '{tx.category}' is at {evaluation['percentage']}% "
                    f"of monthly limit ₹{budget.limit_amount:.2f}."
                )

        self._transactions[tx.id] = tx
        self.save_to_storage()
        return {"transaction": tx, "warning": budget_warning}

    def delete_transaction(self, tx_id: str) -> Transaction:
        """Removes a transaction by ID."""
        if tx_id not in self._transactions:
            raise RecordNotFoundError(f"Transaction with ID '{tx_id}' was not found.", record_id=tx_id)
        removed = self._transactions.pop(tx_id)
        self.save_to_storage()
        return removed

    def get_transaction(self, tx_id: str) -> Transaction:
        """Retrieves a single transaction by ID."""
        if tx_id not in self._transactions:
            raise RecordNotFoundError(f"Transaction with ID '{tx_id}' was not found.", record_id=tx_id)
        return self._transactions[tx_id]

    def list_transactions(
        self,
        category: Optional[str] = None,
        tx_type: Optional[str] = None,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None,
        account: Optional[str] = None,
        search_query: Optional[str] = None
    ) -> List[Transaction]:
        """Filters transactions based on provided criteria."""
        results = list(self._transactions.values())

        if category:
            cat_norm = category.strip().lower()
            results = [tx for tx in results if tx.category.lower() == cat_norm]

        if tx_type:
            type_norm = tx_type.strip().upper()
            results = [tx for tx in results if tx.get_type() == type_norm]

        if start_date:
            parsed_start = Validator.parse_date(start_date)
            results = [tx for tx in results if tx.date >= parsed_start]

        if end_date:
            parsed_end = Validator.parse_date(end_date)
            results = [tx for tx in results if tx.date <= parsed_end]

        if account:
            acc_norm = account.strip().lower()
            results = [tx for tx in results if tx.account.lower() == acc_norm]

        if search_query:
            query = search_query.strip().lower()
            results = [
                tx for tx in results
                if query in tx.description.lower()
                or query in tx.category.lower()
                or any(query in tag for tag in tx.tags)
            ]

        # Return sorted descending by date
        return sorted(results, key=lambda x: x.date, reverse=True)

    # ---------------------------------------------------------
    # Account & Balance Management
    # ---------------------------------------------------------

    def create_account(self, name: str, account_type: str = "SAVINGS", initial_balance: Any = 0.0, description: str = "") -> Account:
        """Registers a new financial account."""
        key = name.strip().lower()
        if key in self._accounts:
            raise ValidationError(f"Account '{name}' already exists.")
        acc = Account(name=name, account_type=account_type, initial_balance=initial_balance, description=description)
        self._accounts[key] = acc
        self.save_to_storage()
        return acc

    def list_accounts(self) -> List[Account]:
        """Returns list of registered accounts."""
        return sorted(list(self._accounts.values()), key=lambda a: a.name)

    def calculate_account_balance(self, account_name: str) -> Decimal:
        """Calculates current balance for an account (initial balance + net signed transactions)."""
        key = account_name.strip().lower()
        acc = self._accounts.get(key)
        balance = acc.initial_balance if acc else Decimal("0.00")

        for tx in self._transactions.values():
            if tx.account.lower() == key:
                balance += tx.signed_amount()

        return balance

    def get_all_balances(self) -> Dict[str, Dict[str, Any]]:
        """Returns current balance breakdown across all registered accounts."""
        balances = {}
        for key, acc in self._accounts.items():
            bal = self.calculate_account_balance(acc.name)
            balances[acc.name] = {
                "name": acc.name,
                "type": acc.account_type,
                "initial_balance": float(acc.initial_balance),
                "current_balance": float(bal)
            }
        return balances

    # ---------------------------------------------------------
    # Budget Management
    # ---------------------------------------------------------

    def set_budget(self, category: str, limit_amount: Any, warning_threshold: float = 0.80) -> Budget:
        """Configures or updates a monthly budget cap for a category."""
        budget = Budget(category=category, limit_amount=limit_amount, warning_threshold=warning_threshold)
        self._budgets[budget.category.lower()] = budget
        self.save_to_storage()
        return budget

    def delete_budget(self, category: str) -> Budget:
        """Removes a category budget."""
        key = category.strip().lower()
        if key not in self._budgets:
            raise RecordNotFoundError(f"Budget for category '{category}' does not exist.")
        removed = self._budgets.pop(key)
        self.save_to_storage()
        return removed

    def list_budgets(self) -> List[Budget]:
        """Returns all configured budgets."""
        return sorted(list(self._budgets.values()), key=lambda b: b.category)

    def get_category_spending(self, category: str, month: Optional[int] = None, year: Optional[int] = None) -> Decimal:
        """Calculates total expense for a specific category within a given month/year."""
        target_month = month or date.today().month
        target_year = year or date.today().year

        cat_norm = category.strip().lower()
        total = Decimal("0.00")

        for tx in self._transactions.values():
            if tx.get_type() == "EXPENSE" and tx.category.lower() == cat_norm:
                if tx.date.month == target_month and tx.date.year == target_year:
                    total += tx.amount

        return total

    def evaluate_all_budgets(self, month: Optional[int] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Evaluates spending status for all configured category budgets."""
        target_month = month or date.today().month
        target_year = year or date.today().year

        evaluations = []
        for budget in self.list_budgets():
            spent = self.get_category_spending(budget.category, month=target_month, year=target_year)
            ev = budget.evaluate(spent)
            ev["month"] = target_month
            ev["year"] = target_year
            evaluations.append(ev)

        return evaluations

    # ---------------------------------------------------------
    # CSV Integration
    # ---------------------------------------------------------

    def export_to_csv(self, file_path: str) -> int:
        """Exports all transactions to a CSV file."""
        return CSVHandler.export_transactions(list(self._transactions.values()), file_path)

    def import_from_csv(self, file_path: str) -> Dict[str, Any]:
        """Imports transactions from a CSV file, skipping duplicates by ID."""
        parsed, errors = CSVHandler.import_transactions(file_path)
        imported_count = 0
        duplicate_count = 0

        for tx in parsed:
            if tx.id in self._transactions:
                duplicate_count += 1
            else:
                self._transactions[tx.id] = tx
                imported_count += 1

        if imported_count > 0:
            self.save_to_storage()

        return {
            "total_parsed": len(parsed),
            "imported": imported_count,
            "duplicates_skipped": duplicate_count,
            "errors": errors
        }
