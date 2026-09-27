"""
Unit tests for data persistence, JSON repository, and CSV import/export handlers.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from decimal import Decimal
from fintrack.storage.repository import JSONRepository
from fintrack.storage.csv_handler import CSVHandler
from fintrack.models.transaction import IncomeTransaction, ExpenseTransaction


class TestStorageLayer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "fintrack_test.json"
        self.repo = JSONRepository(str(self.db_path))

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_json_save_and_reload(self):
        test_payload = {
            "version": "1.0",
            "accounts": [{"name": "Bank", "account_type": "CHECKING", "initial_balance": 1000.0, "description": ""}],
            "budgets": [{"category": "Dining", "limit_amount": 2500.0, "warning_threshold": 0.8, "month": None, "year": None}],
            "transactions": [
                {
                    "id": "tx-test-01",
                    "type": "EXPENSE",
                    "category": "Dining",
                    "amount": 450.0,
                    "date": "2026-09-10",
                    "account": "Bank",
                    "description": "Lunch meeting",
                    "tags": ["food"]
                }
            ]
        }

        self.repo.save_data(test_payload)
        reloaded = self.repo.load_data()

        self.assertEqual(len(reloaded["transactions"]), 1)
        self.assertEqual(reloaded["transactions"][0]["id"], "tx-test-01")
        self.assertEqual(reloaded["transactions"][0]["amount"], 450.0)

    def test_csv_export_and_import_cycle(self):
        tx1 = IncomeTransaction(5000.0, "Consulting", "2026-09-01", "Client payment", "Bank", {"freelance"})
        tx2 = ExpenseTransaction(300.0, "Coffee", "2026-09-02", "Cafe drinks", "Cash", {"leisure"})

        csv_file = Path(self.test_dir) / "exported_tx.csv"
        exported_count = CSVHandler.export_transactions([tx1, tx2], str(csv_file))
        self.assertEqual(exported_count, 2)
        self.assertTrue(csv_file.exists())

        # Now import back
        imported_txs, errors = CSVHandler.import_transactions(str(csv_file))
        self.assertEqual(len(imported_txs), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(imported_txs[0].category, "Consulting")
        self.assertEqual(imported_txs[1].category, "Coffee")

    def test_csv_import_handles_corrupt_row_gracefully(self):
        corrupt_csv = Path(self.test_dir) / "bad_data.csv"
        with open(corrupt_csv, "w", encoding="utf-8") as f:
            f.write("id,type,category,amount,date,account,description,tags\n")
            f.write("tx-ok,INCOME,Salary,1000.00,2026-09-01,Bank,Valid salary,job\n")
            f.write("tx-bad,INVALID_TYPE,Food,invalid_amount,not-a-date,Bank,Bad row,bad\n")

        imported_txs, errors = CSVHandler.import_transactions(str(corrupt_csv))
        self.assertEqual(len(imported_txs), 1)  # Only the valid row is imported
        self.assertEqual(len(errors), 1)        # Bad row recorded in error log
        self.assertEqual(errors[0]["row"], 3)


if __name__ == "__main__":
    unittest.main()
