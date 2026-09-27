"""
Budget models for tracking category-wise monthly limits and alert thresholds.
"""

from decimal import Decimal
from typing import Dict, Any, Union
from fintrack.core.validator import Validator


class BudgetStatus:
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    EXCEEDED = "EXCEEDED"


class Budget:
    """
    Represents a spending limit threshold for a specific category within a monthly cycle.
    """

    def __init__(
        self,
        category: str,
        limit_amount: Union[Decimal, float, str],
        warning_threshold: float = 0.80,
        month: int = None,
        year: int = None
    ):
        self._category = Validator.validate_category(category)
        self._limit_amount = Validator.parse_amount(limit_amount, field_name="Budget Limit")

        if not (0.10 <= float(warning_threshold) <= 1.00):
            raise ValueError("Warning threshold must be between 0.10 (10%) and 1.00 (100%).")
        self._warning_threshold = float(warning_threshold)

        self._month = month
        self._year = year

    @property
    def category(self) -> str:
        return self._category

    @property
    def limit_amount(self) -> Decimal:
        return self._limit_amount

    @property
    def warning_threshold(self) -> float:
        return self._warning_threshold

    @property
    def month(self) -> int:
        return self._month

    @property
    def year(self) -> int:
        return self._year

    def evaluate(self, total_spent: Union[Decimal, float]) -> Dict[str, Any]:
        """
        Evaluates current spending against the budget limit.
        Returns a dictionary containing spent, remaining, percentage, and health status.
        """
        spent = Decimal(str(total_spent)) if not isinstance(total_spent, Decimal) else total_spent
        percentage = (spent / self._limit_amount * Decimal("100.00")) if self._limit_amount > 0 else Decimal("0.00")
        remaining = self._limit_amount - spent

        if spent >= self._limit_amount:
            status = BudgetStatus.EXCEEDED
        elif float(percentage) >= (self._warning_threshold * 100):
            status = BudgetStatus.WARNING
        else:
            status = BudgetStatus.HEALTHY

        return {
            "category": self._category,
            "limit": float(self._limit_amount),
            "spent": float(spent),
            "remaining": float(remaining),
            "percentage": round(float(percentage), 1),
            "status": status,
            "is_over": spent > self._limit_amount
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self._category,
            "limit_amount": float(self._limit_amount),
            "warning_threshold": self._warning_threshold,
            "month": self._month,
            "year": self._year
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Budget":
        return cls(
            category=data["category"],
            limit_amount=data["limit_amount"],
            warning_threshold=data.get("warning_threshold", 0.80),
            month=data.get("month"),
            year=data.get("year")
        )

    def __repr__(self) -> str:
        return f"Budget(category='{self._category}', limit={self._limit_amount})"
