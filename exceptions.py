"""
Custom domain exception hierarchy for FinTrack.
Demonstrates custom exception handling, inheritance, and clean error messaging.
"""


class FinTrackError(Exception):
    """Base exception for all FinTrack domain errors."""
    def __init__(self, message: str, error_code: str = "ERR_GENERAL"):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"


class ValidationError(FinTrackError):
    """Raised when user input fails domain validation rules."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, error_code="ERR_VALIDATION")
        self.field = field


class RecordNotFoundError(FinTrackError):
    """Raised when a requested transaction, budget, or account cannot be located."""
    def __init__(self, message: str, record_id: str = None):
        super().__init__(message, error_code="ERR_NOT_FOUND")
        self.record_id = record_id


class InsufficientBalanceError(FinTrackError):
    """Raised when an expense or transfer exceeds available account balance."""
    def __init__(self, message: str, current_balance: float = 0.0, requested_amount: float = 0.0):
        super().__init__(message, error_code="ERR_INSUFFICIENT_FUNDS")
        self.current_balance = current_balance
        self.requested_amount = requested_amount


class BudgetExceededError(FinTrackError):
    """Raised or warned when spending crosses a designated budget threshold."""
    def __init__(self, message: str, category: str = "", limit: float = 0.0, spent: float = 0.0):
        super().__init__(message, error_code="ERR_BUDGET_EXCEEDED")
        self.category = category
        self.limit = limit
        self.spent = spent


class StorageError(FinTrackError):
    """Raised when data serialization, reading, or atomic writing fails."""
    def __init__(self, message: str, path: str = None):
        super().__init__(message, error_code="ERR_STORAGE")
        self.path = path


class FileImportError(FinTrackError):
    """Raised when importing CSV or external records encounters malformed rows."""
    def __init__(self, message: str, line_number: int = None):
        super().__init__(message, error_code="ERR_CSV_IMPORT")
        self.line_number = line_number
