"""
Account model representing financial accounts and wallets.
"""

from decimal import Decimal
from typing import Dict, Any, Union
from fintrack.core.validator import Validator


class Account:
    """
    Represents an individual financial account or storage wallet (e.g., Bank, Cash, Savings).
    """

    VALID_TYPES = ("SAVINGS", "CHECKING", "CASH", "CREDIT_CARD", "INVESTMENT")

    def __init__(
        self,
        name: str,
        account_type: str = "SAVINGS",
        initial_balance: Union[Decimal, float, str] = "0.00",
        description: str = ""
    ):
        self._name = Validator.validate_non_empty(name, "Account Name", max_length=50)
        atype = account_type.strip().upper()
        if atype not in self.VALID_TYPES:
            atype = "SAVINGS"
        self._account_type = atype
        self._initial_balance = Validator.parse_amount(initial_balance) if Decimal(str(initial_balance)) > 0 else Decimal("0.00")
        self._description = description.strip()

    @property
    def name(self) -> str:
        return self._name

    @property
    def account_type(self) -> str:
        return self._account_type

    @property
    def initial_balance(self) -> Decimal:
        return self._initial_balance

    @property
    def description(self) -> str:
        return self._description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "account_type": self._account_type,
            "initial_balance": float(self._initial_balance),
            "description": self._description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        return cls(
            name=data["name"],
            account_type=data.get("account_type", "SAVINGS"),
            initial_balance=data.get("initial_balance", "0.00"),
            description=data.get("description", "")
        )

    def __repr__(self) -> str:
        return f"Account(name='{self._name}', type='{self._account_type}')"
