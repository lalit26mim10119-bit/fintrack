"""
Input validation utilities for FinTrack.
Provides strict checking and formatting for dates, monetary values, and identifiers.
"""

from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Union, Optional, Tuple
from fintrack.core.exceptions import ValidationError


class Validator:
    """Provides reusable domain validation methods."""

    DATE_FORMATS = ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y")

    @classmethod
    def parse_amount(cls, value: Union[str, int, float, Decimal], field_name: str = "Amount") -> Decimal:
        """
        Parses and validates a monetary amount.
        Ensures value is positive, finite, and rounded to two decimal places.
        """
        if value is None:
            raise ValidationError(f"{field_name} cannot be empty.", field=field_name)

        try:
            if isinstance(value, float):
                # Convert float through string representation to prevent binary float inaccuracies
                amount = Decimal(str(round(value, 2)))
            else:
                amount = Decimal(str(value).strip())
        except (InvalidOperation, TypeError, ValueError):
            raise ValidationError(f"{field_name} must be a valid numeric value.", field=field_name)

        if amount.is_nan() or amount.is_infinite():
            raise ValidationError(f"{field_name} must be a finite number.", field=field_name)

        if amount <= Decimal("0.00"):
            raise ValidationError(f"{field_name} must be strictly greater than 0.00.", field=field_name)

        # Quantize to 2 decimal places
        return amount.quantize(Decimal("0.01"))

    @classmethod
    def parse_date(cls, value: Union[str, date, datetime], field_name: str = "Date") -> date:
        """
        Parses multiple standard date string formats into a datetime.date object.
        """
        if value is None:
            return date.today()

        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value

        cleaned = str(value).strip()
        if not cleaned or cleaned.lower() in ("today", "now"):
            return date.today()

        for fmt in cls.DATE_FORMATS:
            try:
                parsed = datetime.strptime(cleaned, fmt).date()
                return parsed
            except ValueError:
                continue

        raise ValidationError(
            f"Invalid {field_name} format '{value}'. Accepted formats: YYYY-MM-DD or DD-MM-YYYY.",
            field=field_name
        )

    @classmethod
    def validate_non_empty(cls, value: str, field_name: str, max_length: int = 120) -> str:
        """Validates that a string is non-empty and does not exceed maximum length."""
        if not value or not str(value).strip():
            raise ValidationError(f"{field_name} cannot be empty.", field=field_name)

        sanitized = str(value).strip()
        if len(sanitized) > max_length:
            raise ValidationError(
                f"{field_name} exceeds maximum length of {max_length} characters.",
                field=field_name
            )
        return sanitized

    @classmethod
    def validate_category(cls, category: str) -> str:
        """Validates and normalizes category names."""
        cleaned = cls.validate_non_empty(category, "Category", max_length=50)
        return cleaned.title()

    @classmethod
    def parse_tags(cls, tags_input: Union[str, list, tuple, set]) -> set:
        """Normalizes tags into a clean set of lowercase strings."""
        if not tags_input:
            return set()

        if isinstance(tags_input, (list, tuple, set)):
            raw_tags = tags_input
        else:
            raw_tags = str(tags_input).replace(";", ",").split(",")

        sanitized = set()
        for t in raw_tags:
            tag = str(t).strip().lower()
            if tag and len(tag) <= 30:
                sanitized.add(tag)
        return sanitized
