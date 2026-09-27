"""
Storage repository implementations for FinTrack.
Demonstrates abstract base classes, JSON serialization, atomic file writing, and persistence.
"""

from abc import ABC, abstractmethod
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from fintrack.core.exceptions import StorageError


class DataRepository(ABC):
    """Abstract interface defining required storage operations."""

    @abstractmethod
    def load_data(self) -> Dict[str, Any]:
        """Loads and parses raw domain data from storage."""
        pass

    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> None:
        """Persists domain data into storage."""
        pass


class JSONRepository(DataRepository):
    """
    JSON file persistence with atomic write semantics and automatic backup.
    Ensures data integrity even during unexpected termination.
    """

    DEFAULT_DATA: Dict[str, Any] = {
        "version": "1.0",
        "accounts": [
            {"name": "Bank", "account_type": "CHECKING", "initial_balance": 0.0, "description": "Primary bank account"},
            {"name": "Cash", "account_type": "CASH", "initial_balance": 0.0, "description": "Physical cash wallet"},
            {"name": "Savings", "account_type": "SAVINGS", "initial_balance": 0.0, "description": "Emergency savings reserve"}
        ],
        "budgets": [],
        "transactions": []
    }

    def __init__(self, file_path: str = None):
        if file_path is None:
            # Default storage path inside project root data directory
            base_dir = Path(__file__).resolve().parent.parent.parent / "data"
            self.file_path = base_dir / "fintrack_db.json"
        else:
            self.file_path = Path(file_path)

        self.backup_path = self.file_path.with_suffix(".json.bak")
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        """Creates directory and initializes empty database if not present."""
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            if not self.file_path.exists():
                self.save_data(self.DEFAULT_DATA)
        except Exception as exc:
            raise StorageError(f"Failed to initialize storage at {self.file_path}: {exc}", path=str(self.file_path))

    def load_data(self) -> Dict[str, Any]:
        """Loads database from JSON file. Falls back to backup if corrupted."""
        if not self.file_path.exists():
            return self.DEFAULT_DATA.copy()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                return content
        except (json.JSONDecodeError, OSError) as exc:
            # Try recovering from backup
            if self.backup_path.exists():
                try:
                    with open(self.backup_path, "r", encoding="utf-8") as bf:
                        recovered = json.load(bf)
                        return recovered
                except Exception:
                    pass
            raise StorageError(f"Database file is corrupted or unreadable: {exc}", path=str(self.file_path))

    def save_data(self, data: Dict[str, Any]) -> None:
        """
        Atomically saves data by writing to a temporary file then renaming.
        Prevents corrupt files from partial writes.
        """
        temp_path = self.file_path.with_suffix(".json.tmp")
        try:
            # If current file exists, copy to backup
            if self.file_path.exists():
                try:
                    with open(self.file_path, "r", encoding="utf-8") as src, open(self.backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                except Exception:
                    pass  # Non-fatal if backup creation fails

            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Atomic replace
            os.replace(temp_path, self.file_path)
        except Exception as exc:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise StorageError(f"Failed to save data: {exc}", path=str(self.file_path))
