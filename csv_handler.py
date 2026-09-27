"""
CSV import and export services for transactions.
Demonstrates file I/O, error handling, CSV dialect handling, and row-level validation.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any, Tuple
from fintrack.models.transaction import Transaction, IncomeTransaction, ExpenseTransaction
from fintrack.core.exceptions import FileImportError, ValidationError


class CSVHandler:
    """Manages reading and writing transaction records in standard CSV format."""

    CSV_HEADERS = ["id", "type", "category", "amount", "date", "account", "description", "tags"]

    @classmethod
    def export_transactions(cls, transactions: List[Transaction], output_path: str) -> int:
        """
        Exports a list of transactions to a CSV file.
        Returns the number of exported records.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.CSV_HEADERS)
            writer.writeheader()

            count = 0
            for tx in transactions:
                writer.writerow({
                    "id": tx.id,
                    "type": tx.get_type(),
                    "category": tx.category,
                    "amount": f"{float(tx.amount):.2f}",
                    "date": tx.date.isoformat(),
                    "account": tx.account,
                    "description": tx.description,
                    "tags": ";".join(sorted(list(tx.tags)))
                })
                count += 1

        return count

    @classmethod
    def import_transactions(cls, file_path: str) -> Tuple[List[Transaction], List[Dict[str, Any]]]:
        """
        Imports transaction records from a CSV file.
        Returns a tuple of (successfully_parsed_transactions, list_of_row_errors).
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"CSV import file not found at: {path}")

        parsed_transactions: List[Transaction] = []
        errors: List[Dict[str, Any]] = []

        with open(path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Normalize headers
            if not reader.fieldnames:
                raise FileImportError("CSV file is empty or missing headers.")

            row_num = 1
            for row in reader:
                row_num += 1
                # Skip blank lines
                if not any(row.values()):
                    continue

                try:
                    # Clean dictionary keys
                    clean_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                    
                    tx_type = clean_row.get("type", "").upper()
                    if tx_type not in ("INCOME", "EXPENSE"):
                        raise ValidationError(f"Invalid type '{tx_type}'. Must be 'INCOME' or 'EXPENSE'.")

                    amount_val = clean_row.get("amount")
                    category_val = clean_row.get("category", "General")
                    date_val = clean_row.get("date")
                    account_val = clean_row.get("account", "Default")
                    desc_val = clean_row.get("description", "Imported transaction")
                    tags_val = clean_row.get("tags", "")
                    tx_id = clean_row.get("id")

                    if tx_type == "INCOME":
                        tx = IncomeTransaction(
                            amount=amount_val,
                            category=category_val,
                            date_val=date_val,
                            account=account_val,
                            description=desc_val,
                            tags=tags_val,
                            tx_id=tx_id
                        )
                    else:
                        tx = ExpenseTransaction(
                            amount=amount_val,
                            category=category_val,
                            date_val=date_val,
                            account=account_val,
                            description=desc_val,
                            tags=tags_val,
                            tx_id=tx_id
                        )

                    parsed_transactions.append(tx)

                except Exception as exc:
                    errors.append({
                        "row": row_num,
                        "data": row,
                        "error": str(exc)
                    })

        return parsed_transactions, errors
