"""
Transaction models representing monetary inflows and outflows.
Demonstrates OOP concepts: inheritance, polymorphism, encapsulation, and magic methods.
"""

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
import uuid
from typing import Dict, Any, Set, Union
from fintrack.core.validator import Validator


class Transaction(ABC):
    """
    Abstract Base Class for all financial transactions.
    Demonstrates encapsulation with properties and getters/setters.
    """

    def __init__(
        self,
        amount: Union[Decimal, float, str],
        category: str,
        date_val: Union[date, str] = None,
        description: str = "General Transaction",
        account: str = "Default",
        tags: Union[Set[str], list, str] = None,
        tx_id: str = None
    ):
        self._id = tx_id or f"tx-{uuid.uuid4().hex[:8]}"
        self._amount = Validator.parse_amount(amount)
        self._category = Validator.validate_category(category)
        self._date = Validator.parse_date(date_val)
        self._description = Validator.validate_non_empty(description, "Description", max_length=200)
        self._account = Validator.validate_non_empty(account, "Account", max_length=50)
        self._tags = Validator.parse_tags(tags)

    @property
    def id(self) -> str:
        return self._id

    @property
    def amount(self) -> Decimal:
        return self._amount

    @property
    def category(self) -> str:
        return self._category

    @property
    def date(self) -> date:
        return self._date

    @property
    def description(self) -> str:
        return self._description

    @property
    def account(self) -> str:
        return self._account

    @property
    def tags(self) -> Set[str]:
        return set(self._tags)

    @abstractmethod
    def get_type(self) -> str:
        """Returns the transaction classification type (e.g., 'INCOME' or 'EXPENSE')."""
        pass

    @abstractmethod
    def signed_amount(self) -> Decimal:
        """Returns positive for income and negative for expense."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the transaction model to a dictionary suitable for JSON."""
        return {
            "id": self._id,
            "type": self.get_type(),
            "category": self._category,
            "amount": float(self._amount),
            "date": self._date.isoformat(),
            "account": self._account,
            "description": self._description,
            "tags": sorted(list(self._tags))
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Factory constructor instantiating the appropriate concrete transaction subclass."""
        tx_type = data.get("type", "").upper()
        if tx_type == "INCOME":
            return IncomeTransaction(
                amount=data["amount"],
                category=data["category"],
                date_val=data["date"],
                description=data.get("description", "Income"),
                account=data.get("account", "Default"),
                tags=data.get("tags", []),
                tx_id=data.get("id")
            )
        elif tx_type == "EXPENSE":
            return ExpenseTransaction(
                amount=data["amount"],
                category=data["category"],
                date_val=data["date"],
                description=data.get("description", "Expense"),
                account=data.get("account", "Default"),
                tags=data.get("tags", []),
                tx_id=data.get("id")
            )
        else:
            raise ValueError(f"Unknown transaction type: '{tx_type}'")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transaction):
            return False
        return self._id == other._id

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self._id}', amount={self._amount}, category='{self._category}')"

    def __str__(self) -> str:
        return f"[{self.get_type()}] {self._date} | {self._category:<15} | ₹{self._amount:>9.2f} | {self._description}"


class IncomeTransaction(Transaction):
    """Concrete transaction representing funds received into an account."""

    def get_type(self) -> str:
        return "INCOME"

    def signed_amount(self) -> Decimal:
        return self._amount


class ExpenseTransaction(Transaction):
    """Concrete transaction representing funds expended from an account."""

    def get_type(self) -> str:
        return "EXPENSE"

    def signed_amount(self) -> Decimal:
        return -self._amount
