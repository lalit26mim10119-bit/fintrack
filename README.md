# FinTrack : Personal Finance & Budget Analytics CLI

> **Course**: Python Essentials  
> **Evaluation Mode**: Evaluated Course Project  
> **Environment**: Command Line Interface (CLI) & Interactive Shell  
> **Dependencies**: 100% Python Standard Library (Zero External Dependencies)

---

## 1. Project Overview

**FinTrack** is an enterprise-grade, lightweight personal finance management and budget analytics system designed to operate directly within terminal environments. Engineered specifically to demonstrate core Python software engineering principles, FinTrack bridges the gap between complex cloud-dependent budgeting platforms and unstructured spreadsheets.

It enables users to track multi-account liquid balances, categorize income and expenditure, configure category-level monthly budgets with proactive alerting, analyze cashflow trajectories, and visualize spending habits via terminal-native ASCII bar charts.

### Key Highlights
- **100% Zero External Dependencies**: Requires zero `pip install` commands. Runs natively on Python 3.8+ on Windows, Linux, and macOS.
- **Precision Financial Arithmetic**: Implements Python's `decimal.Decimal` to avoid floating-point binary representation errors in financial calculations.
- **Fail-Safe Atomic Persistence**: Employs atomic file replacement and automatic snapshot backups to prevent JSON database corruption during unexpected termination.
- **Dual Execution Paradigms**: Features both an interactive text menu system (`--interactive`) and a headless subcommand CLI (`fintrack <command>`) for automation and grading scripts.
- **Automated Validation & Custom Exceptions**: Rigorous input sanitization, date format tolerance (`YYYY-MM-DD` and `DD-MM-YYYY`), and descriptive domain exceptions.

---

## 2. Features

### Core Functional Modules
1. **Transaction Management Module**
   - Record income and expense entries with amount, category, date, payment account, description, and tags.
   - Dynamic search and multi-parameter filtering (by date range, category, transaction type, or keywords).
   - Deletion and validation safeguards preventing negative amounts or zero transactions.
2. **Multi-Account & Balance Reconciliation Module**
   - Multiple asset wallets (e.g., Checking/Bank, Physical Cash, Emergency Savings, Credit Accounts).
   - Dynamic net portfolio valuation computed from opening balances and signed transaction deltas.
3. **Proactive Budget Monitoring & Alerting Module**
   - Configurable monthly category caps with adjustable warning thresholds (e.g., 80%).
   - Immediate feedback upon expense creation: `HEALTHY`, `[!] WARNING`, or `[X] EXCEEDED`.
4. **Analytics & Terminal Data Visualization Module**
   - Aggregated metrics: Gross Inflow, Gross Outflow, Net Liquid Savings, and Savings Rate (%).
   - Category-wise expense percentage shares.
   - Month-over-month cashflow history.
   - Pure terminal ASCII horizontal bar charts for quick visual inspection.
5. **Data Interchange & Reporting Module**
   - Import transactions from external CSV files with row-level error reporting.
   - Export full transaction ledgers to CSV.
   - Comprehensive formatted financial statements printable to stdout or exported to text files.

---

## 3. Technologies & Tools Used

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | Python 3.8+ | Universal, modern, cross-platform language runtime |
| **Numeric Engine** | `decimal` | Fixed-point arithmetic prevents binary float rounding inaccuracies |
| **CLI & Parsing** | `argparse` | Standard library CLI argument parsing supporting subcommands |
| **Data Serialization**| `json` & `csv` | Human-readable persistence with standard data interchange |
| **File I/O Safety** | `os.replace`, `pathlib` | Atomic filesystem updates preventing database file corruption |
| **Date Processing** | `datetime` | Multi-format date parsing (`YYYY-MM-DD`, `DD-MM-YYYY`) |
| **Testing** | `unittest` | Built-in test runner for unit tests and edge cases |

---

## 4. Folder & Package Structure

```
fintrack/
├── .gitignore                      # Git ignore specifications
├── README.md                       # Main project setup, usage, and reference guide
├── statement.md                    # Problem statement, scope, target users, and features
├── PROJECT_REPORT.md               # 15-section comprehensive project evaluation report
├── generate_report_pdf.py          # Automated report compilation utility
├── requirements.txt                # Specification indicating standard library zero-deps
├── main.py                         # Unified entry point for interactive and CLI execution
├── fintrack/                       # Core application package
│   ├── __init__.py                 # Package initializer
│   ├── models/                     # OOP domain entities
│   │   ├── __init__.py
│   │   ├── transaction.py          # Transaction, IncomeTransaction, ExpenseTransaction
│   │   ├── budget.py               # Budget model, threshold evaluation, health statuses
│   │   └── account.py              # Financial account / wallet entity
│   ├── core/                       # Core orchestration and rules
│   │   ├── __init__.py
│   │   ├── exceptions.py           # Custom domain exception hierarchy
│   │   ├── validator.py            # Input sanitization and format validators
│   │   └── engine.py               # FinanceEngine facade coordinating domain logic
│   ├── storage/                    # Persistence layer
│   │   ├── __init__.py
│   │   ├── repository.py           # Abstract DataRepository & JSONRepository with atomic writes
│   │   └── csv_handler.py          # CSV import and export handler with row error logging
│   ├── analytics/                  # Analytics and visualization
│   │   ├── __init__.py
│   │   └── reporter.py             # FinancialReporter (aggregates, trends, ASCII charts)
│   └── cli/                        # Command-line presentation layer
│       ├── __init__.py
│       ├── argument_parser.py      # argparse subcommand tree
│       ├── interactive.py          # Interactive terminal menu shell
│       └── formatting.py           # Pure Python table renderer & border styling
├── tests/                          # Automated unit test suite
│   ├── __init__.py
│   ├── test_models.py              # Model instantiation, polymorphism & validation tests
│   ├── test_engine.py              # Engine operations, budget alerts & transactions
│   ├── test_storage.py             # Atomic write, JSON recovery, and CSV cycle tests
│   └── test_analytics.py           # Analytics calculation & ASCII chart rendering tests
└── data/
    └── sample_transactions.csv     # Sample CSV dataset for rapid testing
```

---

## 5. Installation & Execution Guide

### Prerequisites
- Python 3.8 or higher installed on your system.
- Terminal environment (PowerShell, Command Prompt, bash, zsh, etc.).
- No external packages need to be installed.

### Step 1: Clone or Navigate to the Repository
```bash
git clone https://github.com/{your-username}/fintrack.git
cd fintrack
```

### Step 2: Verify Python Environment
Ensure your Python version is 3.8+:
```bash
python --version
```

### Step 3: Run the Project

#### Mode A: Interactive Terminal Dashboard (Recommended for Users)
Run the application without arguments (or with `--interactive`):
```bash
python main.py
```
This launches a guided, numbered menu system allowing you to inspect balances, record transactions, review budgets, and generate visual charts.

#### Mode B: Headless Command Line (Ideal for Evaluators & Scripting)
You can invoke any subcommand directly from your terminal:

1. **Initialize or reset database**:
   ```bash
   python main.py init
   ```

2. **Import sample transactions**:
   ```bash
   python main.py import -i data/sample_transactions.csv
   ```

3. **Record an Income transaction**:
   ```bash
   python main.py add-income -a 50000.00 -c Salary -m "Monthly engineering salary" -w Bank
   ```

4. **Record an Expense transaction**:
   ```bash
   python main.py add-expense -a 1200.00 -c Dining -m "Dinner with teammates" -w Cash -t "social;leisure"
   ```

5. **Configure a Category Budget**:
   ```bash
   python main.py budget set -c Dining -l 3000.00 -w 0.80
   ```

6. **Check Budget Status**:
   ```bash
   python main.py budget status
   ```

7. **List & Filter Transactions**:
   ```bash
   python main.py list
   python main.py list --type EXPENSE -c Dining
   python main.py list -s "salary"
   ```

8. **View Account Balances**:
   ```bash
   python main.py account balance
   ```

9. **View Financial Analytics & ASCII Chart**:
   ```bash
   python main.py analytics overview
   python main.py analytics breakdown
   python main.py analytics trends
   ```

10. **Generate Complete Financial Statement**:
    ```bash
    python main.py report
    python main.py report -o data/financial_report.txt
    ```

11. **Export Ledgers to CSV**:
    ```bash
    python main.py export -o data/my_export.csv
    ```

---

## 6. Instructions for Testing

FinTrack includes a comprehensive automated unit test suite using Python's standard `unittest` framework.

### Run All Unit Tests
From the root project directory, execute:
```bash
python -m unittest discover tests -v
```

### Expected Output
```
test_account_creation_and_attributes (tests.test_models.TestAccountModel) ... ok
test_budget_evaluation_exceeded (tests.test_models.TestBudgetModel) ... ok
test_budget_evaluation_healthy (tests.test_models.TestBudgetModel) ... ok
test_budget_evaluation_warning (tests.test_models.TestBudgetModel) ... ok
test_expense_transaction_creation (tests.test_models.TestTransactionModels) ... ok
test_income_transaction_creation (tests.test_models.TestTransactionModels) ... ok
test_invalid_date_format_raises_validation_error (tests.test_models.TestTransactionModels) ... ok
test_negative_or_zero_amount_raises_validation_error (tests.test_models.TestTransactionModels) ... ok
test_serialization_roundtrip (tests.test_models.TestTransactionModels) ... ok
test_add_income_and_expense (tests.test_engine.TestFinanceEngine) ... ok
test_budget_threshold_warning (tests.test_engine.TestFinanceEngine) ... ok
test_delete_transaction (tests.test_engine.TestFinanceEngine) ... ok
test_list_and_filter_transactions (tests.test_engine.TestFinanceEngine) ... ok
test_csv_export_and_import_cycle (tests.test_storage.TestStorageLayer) ... ok
test_csv_import_handles_corrupt_row_gracefully (tests.test_storage.TestStorageLayer) ... ok
test_json_save_and_reload (tests.test_storage.TestStorageLayer) ... ok
test_ascii_bar_chart_generation (tests.test_analytics.TestFinancialReporter) ... ok
test_category_breakdown (tests.test_analytics.TestFinancialReporter) ... ok
test_full_text_report_generation (tests.test_analytics.TestFinancialReporter) ... ok
test_monthly_trends (tests.test_analytics.TestFinancialReporter) ... ok
test_overview_calculations (tests.test_analytics.TestFinancialReporter) ... ok

----------------------------------------------------------------------
Ran 21 tests in 0.045s

OK
```

---

## 7. Terminal Walkthrough & Screenshots

### Interactive Menu Shell
```
==================================================================
          FINTRACK : PERSONAL FINANCE & BUDGET ANALYTICS          
                  Course: Python Essentials                       
==================================================================

  1. Dashboard & Account Balances
  2. Record New Expense (-)
  3. Record New Income (+)
  4. View & Filter Transactions
  5. Budget Management & Alerts
  6. Analytics & Category Charts
  7. Monthly Cashflow Trends
  8. Import Transactions from CSV
  9. Export Transactions to CSV
 10. Generate Financial Statement Report
  0. Save & Exit
------------------------------------------------------------------
```

### Table View: Transactions
```
┌───────────┬─────────┬────────────┬─────────────┬────────────┬─────────┬───────────────────────────┐
│    ID     │  Type   │    Date    │  Category   │   Amount   │ Account │ Description               │
├───────────┼─────────┼────────────┼─────────────┼────────────┼─────────┼───────────────────────────┤
│ tx-001    │ INCOME  │ 2026-09-01 │ Salary      │ ₹45,000.00 │ Bank    │ Monthly software engine...│
│ tx-002    │ EXPENSE │ 2026-09-02 │ Rent        │ ₹12,000.00 │ Bank    │ Apartment rent payment    │
│ tx-003    │ EXPENSE │ 2026-09-04 │ Groceries   │  ₹3,450.50 │ Cash    │ Supermarket restocking    │
│ tx-005    │ INCOME  │ 2026-09-08 │ Freelance   │  ₹8,500.00 │ Bank    │ Client website milestone  │
└───────────┴─────────┴────────────┴─────────────┴────────────┴─────────┴───────────────────────────┘
```

### Category Spending ASCII Visualization
```
--- EXPENSE DISTRIBUTION ---
Rent                 | ██████████████████████████████ ₹12,000.00
Groceries            | ████████                       ₹3,450.50
Utilities            | ████                           ₹1,850.00
Dining               | ███                            ₹1,250.00
Transportation       | ██                             ₹1,100.00
Books                | ██                               ₹950.00
```

---

## 8. Author & Academic Submission Notice

- **Project**: Python Essentials Evaluated Course Project
- **Platform**: VITyarthi
- **License**: MIT Academic Open Source
- **Repository Format**: `https://github.com/{github-username}/{repo-name}`
- **Visibility**: Public
