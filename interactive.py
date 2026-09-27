"""
Interactive terminal dashboard and menu interface for FinTrack.
Provides an intuitive, guided experience for non-technical users and live demonstrations.
"""

import sys
from datetime import date
from fintrack.core.engine import FinanceEngine
from fintrack.analytics.reporter import FinancialReporter
from fintrack.cli.formatting import TerminalFormatter
from fintrack.core.exceptions import FinTrackError


class InteractiveSession:
    """Manages the interactive terminal menu loop and user prompts."""

    def __init__(self, engine: FinanceEngine):
        self.engine = engine

    def run(self) -> None:
        """Main interaction loop."""
        while True:
            TerminalFormatter.print_banner(
                "FINTRACK : PERSONAL FINANCE & BUDGET ANALYTICS",
                "Course: Python Essentials | Terminal Edition"
            )
            print("  1. Dashboard & Account Balances")
            print("  2. Record New Expense (-)")
            print("  3. Record New Income (+)")
            print("  4. View & Filter Transactions")
            print("  5. Budget Management & Alerts")
            print("  6. Analytics & Category Charts")
            print("  7. Monthly Cashflow Trends")
            print("  8. Import Transactions from CSV")
            print("  9. Export Transactions to CSV")
            print(" 10. Generate Financial Statement Report")
            print("  0. Save & Exit")
            print("-" * 66)

            choice = input("Select an option [0-10]: ").strip()

            try:
                if choice == "1":
                    self.show_dashboard()
                elif choice == "2":
                    self.prompt_add_expense()
                elif choice == "3":
                    self.prompt_add_income()
                elif choice == "4":
                    self.prompt_list_transactions()
                elif choice == "5":
                    self.manage_budgets()
                elif choice == "6":
                    self.show_analytics()
                elif choice == "7":
                    self.show_monthly_trends()
                elif choice == "8":
                    self.prompt_import_csv()
                elif choice == "9":
                    self.prompt_export_csv()
                elif choice == "10":
                    self.generate_report()
                elif choice in ("0", "exit", "quit", "q"):
                    print("\nAll data persisted securely. Thank you for using FinTrack!")
                    break
                else:
                    print("\nInvalid choice. Please select an option between 0 and 10.")
            except (KeyboardInterrupt, EOFError):
                print("\n\nSession terminated by user. Goodbye!")
                break
            except FinTrackError as err:
                print(f"\n[Operation Failed]: {err}")
            except Exception as exc:
                print(f"\n[System Error]: {exc}")

            input("\nPress [Enter] to return to the main menu...")

    def show_dashboard(self) -> None:
        """Displays high level portfolio value and balances."""
        print("\n" + "=" * 50)
        print("           ACCOUNT BALANCES OVERVIEW           ")
        print("=" * 50)
        balances = self.engine.get_all_balances()
        headers = ["Account", "Type", "Current Balance"]
        rows = [
            [info["name"], info["type"], TerminalFormatter.format_currency(info["current_balance"])]
            for info in balances.values()
        ]
        print(TerminalFormatter.render_table(headers, rows, ["left", "center", "right"]))
        total_net = sum(info["current_balance"] for info in balances.values())
        print(f"\nTotal Liquid Capital: {TerminalFormatter.format_currency(total_net)}")

        reporter = FinancialReporter(list(self.engine._transactions.values()))
        ov = reporter.calculate_overview()
        print("\nLifetime Cashflow:")
        print(f"  • Inflow  (Income):   {TerminalFormatter.format_currency(ov['total_income'])}")
        print(f"  • Outflow (Expense):  {TerminalFormatter.format_currency(ov['total_expense'])}")
        print(f"  • Net Savings:        {TerminalFormatter.format_currency(ov['net_savings'])} ({ov['savings_rate_pct']}%)")

    def prompt_add_expense(self) -> None:
        """Guides user through logging an expense."""
        print("\n--- Record New Expense ---")
        amount = input("Amount (e.g. 450.00): ").strip()
        category = input("Category (e.g. Food, Groceries, Rent, Utilities): ").strip()
        date_str = input(f"Date [YYYY-MM-DD or DD-MM-YYYY] (leave blank for today: {date.today()}): ").strip()
        account = input("Payment Account [Bank/Cash/Savings] (default: Bank): ").strip() or "Bank"
        description = input("Description/Notes (e.g. Weekly grocery run): ").strip() or "Expense"
        tags = input("Tags (comma-separated, optional): ").strip()

        res = self.engine.add_expense(
            amount=amount,
            category=category,
            date_val=date_str if date_str else None,
            account=account,
            description=description,
            tags=tags
        )
        tx = res["transaction"]
        print(f"\n[OK] Expense saved successfully! ID: {tx.id}")
        if res["warning"]:
            print(f"\n[WARNING] {res['warning']}")

    def prompt_add_income(self) -> None:
        """Guides user through logging an income."""
        print("\n--- Record New Income ---")
        amount = input("Amount (e.g. 50000.00): ").strip()
        category = input("Category (e.g. Salary, Freelance, Dividend, Gift): ").strip()
        date_str = input(f"Date [YYYY-MM-DD or DD-MM-YYYY] (leave blank for today: {date.today()}): ").strip()
        account = input("Receiving Account [Bank/Cash/Savings] (default: Bank): ").strip() or "Bank"
        description = input("Description/Notes: ").strip() or "Income"
        tags = input("Tags (comma-separated, optional): ").strip()

        tx = self.engine.add_income(
            amount=amount,
            category=category,
            date_val=date_str if date_str else None,
            account=account,
            description=description,
            tags=tags
        )
        print(f"\n[OK] Income saved successfully! ID: {tx.id}")

    def prompt_list_transactions(self) -> None:
        """Provides filterable listing of transactions."""
        print("\n--- Filter Transactions ---")
        print("Leave fields blank to skip filter criteria.")
        cat = input("Category filter: ").strip() or None
        t_type = input("Type filter [INCOME / EXPENSE]: ").strip().upper() or None
        query = input("Search keyword (in description/tags): ").strip() or None

        txs = self.engine.list_transactions(category=cat, tx_type=t_type, search_query=query)
        if not txs:
            print("\nNo transactions found matching your criteria.")
            return

        headers = ["ID", "Type", "Date", "Category", "Amount", "Account", "Description"]
        rows = [
            [
                tx.id,
                tx.get_type(),
                str(tx.date),
                tx.category,
                TerminalFormatter.format_currency(tx.amount),
                tx.account,
                (tx.description[:25] + "...") if len(tx.description) > 28 else tx.description
            ]
            for tx in txs[:20]
        ]
        alignments = ["left", "center", "center", "left", "right", "left", "left"]
        print("\n" + TerminalFormatter.render_table(headers, rows, alignments))
        print(f"Displaying {min(len(txs), 20)} of {len(txs)} records.")

    def manage_budgets(self) -> None:
        """Budget review and configuration menu."""
        print("\n--- Budget Management & Alert Status ---")
        print("1. View Current Monthly Budget Status")
        print("2. Set / Update Category Budget Limit")
        sub_choice = input("Select [1 or 2]: ").strip()

        if sub_choice == "1":
            evals = self.engine.evaluate_all_budgets()
            if not evals:
                print("No budgets currently configured.")
                return

            headers = ["Category", "Monthly Limit", "Current Spent", "Remaining", "Used %", "Status"]
            rows = [
                [
                    ev["category"],
                    TerminalFormatter.format_currency(ev["limit"]),
                    TerminalFormatter.format_currency(ev["spent"]),
                    TerminalFormatter.format_currency(ev["remaining"]),
                    f"{ev['percentage']}%",
                    TerminalFormatter.status_tag(ev["status"])
                ]
                for ev in evals
            ]
            print(TerminalFormatter.render_table(headers, rows, ["left", "right", "right", "right", "right", "center"]))

        elif sub_choice == "2":
            cat = input("Category name: ").strip()
            limit = input("Monthly limit (e.g. 5000.00): ").strip()
            warn = input("Warning threshold % [10-100] (default: 80): ").strip()
            warn_factor = (float(warn) / 100.0) if warn.isdigit() else 0.80

            b = self.engine.set_budget(cat, limit, warning_threshold=warn_factor)
            print(f"[OK] Budget for '{b.category}' set to {TerminalFormatter.format_currency(b.limit_amount)}.")

    def show_analytics(self) -> None:
        """Displays category-wise breakdown and ASCII chart."""
        reporter = FinancialReporter(list(self.engine._transactions.values()))
        breakdown = reporter.get_category_breakdown("EXPENSE")
        if not breakdown:
            print("\nNo expense records available to analyze.")
            return

        headers = ["Category", "Amount", "Share %"]
        rows = [
            [b["category"], TerminalFormatter.format_currency(b["amount"]), f"{b['percentage']}%"]
            for b in breakdown
        ]
        print(TerminalFormatter.render_table(headers, rows, ["left", "right", "right"]))
        chart_data = [(b["category"], b["amount"]) for b in breakdown[:6]]
        print(reporter.generate_ascii_bar_chart("EXPENSE BREAKDOWN BY CATEGORY", chart_data))

    def show_monthly_trends(self) -> None:
        """Displays month-by-month financial trajectories."""
        reporter = FinancialReporter(list(self.engine._transactions.values()))
        trends = reporter.get_monthly_trends()
        if not trends:
            print("\nNo transactions recorded to calculate trends.")
            return

        headers = ["Month", "Inflow (Income)", "Outflow (Expense)", "Net Savings", "Savings Rate"]
        rows = [
            [
                t["period"],
                TerminalFormatter.format_currency(t["income"]),
                TerminalFormatter.format_currency(t["expense"]),
                TerminalFormatter.format_currency(t["net"]),
                f"{t['savings_rate']}%"
            ]
            for t in trends
        ]
        print(TerminalFormatter.render_table(headers, rows, ["center", "right", "right", "right", "right"]))

    def prompt_import_csv(self) -> None:
        """Interactive CSV import."""
        path = input("Enter path to CSV file (e.g. data/sample_transactions.csv): ").strip()
        if not path:
            print("Import aborted: no file path provided.")
            return
        res = self.engine.import_from_csv(path)
        print(f"\n[OK] Import Complete!")
        print(f"     Parsed Rows:        {res['total_parsed']}")
        print(f"     Successfully Added: {res['imported']}")
        print(f"     Duplicates Skipped: {res['duplicates_skipped']}")
        if res["errors"]:
            print(f"     Failed Rows:        {len(res['errors'])}")

    def prompt_export_csv(self) -> None:
        """Interactive CSV export."""
        path = input("Enter destination CSV file path (e.g. data/exported_transactions.csv): ").strip()
        if not path:
            path = "data/exported_transactions.csv"
        count = self.engine.export_to_csv(path)
        print(f"\n[OK] Successfully exported {count} transactions to: {path}")

    def generate_report(self) -> None:
        """Renders comprehensive statement and allows saving."""
        reporter = FinancialReporter(list(self.engine._transactions.values()))
        report = reporter.generate_full_text_report()
        print("\n" + report)

        save_choice = input("\nSave report to text file? [y/N]: ").strip().lower()
        if save_choice == "y":
            out = input("Enter file path (default: data/financial_report.txt): ").strip() or "data/financial_report.txt"
            with open(out, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"[OK] Report written to: {out}")
