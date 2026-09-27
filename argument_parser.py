"""
Command-line interface argument parsing using standard library argparse.
Enables full headless execution for automated evaluation and batch scripting.
"""

import argparse
import sys
from pathlib import Path
from fintrack.core.engine import FinanceEngine
from fintrack.analytics.reporter import FinancialReporter
from fintrack.cli.formatting import TerminalFormatter
from fintrack.core.exceptions import FinTrackError


def setup_cli_parser() -> argparse.ArgumentParser:
    """Configures the top-level argument parser and subcommands."""
    parser = argparse.ArgumentParser(
        prog="fintrack",
        description="FinTrack - Personal Finance & Budget Analytics CLI",
        epilog="Use 'fintrack <subcommand> --help' for detailed instructions on any command."
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Launch the interactive text-based dashboard menu"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # --- Subcommand: init ---
    init_parser = subparsers.add_parser("init", help="Initialize or reset database")
    init_parser.add_argument("--reset", action="store_true", help="Reset existing database to blank state")

    # --- Subcommand: add-expense ---
    exp_parser = subparsers.add_parser("add-expense", help="Record an expense transaction")
    exp_parser.add_argument("-a", "--amount", type=float, required=True, help="Expense amount (e.g. 250.50)")
    exp_parser.add_argument("-c", "--category", type=str, required=True, help="Expense category (e.g. Food, Rent)")
    exp_parser.add_argument("-d", "--date", type=str, default=None, help="Date in YYYY-MM-DD or DD-MM-YYYY (default: today)")
    exp_parser.add_argument("-m", "--desc", type=str, default="Expense", help="Description notes")
    exp_parser.add_argument("-w", "--account", type=str, default="Bank", help="Payment account (default: Bank)")
    exp_parser.add_argument("-t", "--tags", type=str, default="", help="Semicolon or comma-separated tags")

    # --- Subcommand: add-income ---
    inc_parser = subparsers.add_parser("add-income", help="Record an income transaction")
    inc_parser.add_argument("-a", "--amount", type=float, required=True, help="Income amount (e.g. 50000.00)")
    inc_parser.add_argument("-c", "--category", type=str, required=True, help="Income category (e.g. Salary, Dividend)")
    inc_parser.add_argument("-d", "--date", type=str, default=None, help="Date in YYYY-MM-DD or DD-MM-YYYY (default: today)")
    inc_parser.add_argument("-m", "--desc", type=str, default="Income", help="Description notes")
    inc_parser.add_argument("-w", "--account", type=str, default="Bank", help="Receiving account (default: Bank)")
    inc_parser.add_argument("-t", "--tags", type=str, default="", help="Semicolon or comma-separated tags")

    # --- Subcommand: list ---
    list_parser = subparsers.add_parser("list", help="List and search transactions")
    list_parser.add_argument("--type", choices=["INCOME", "EXPENSE"], help="Filter by transaction type")
    list_parser.add_argument("-c", "--category", type=str, help="Filter by category")
    list_parser.add_argument("-w", "--account", type=str, help="Filter by account")
    list_parser.add_argument("-s", "--search", type=str, help="Search string in description, category, or tags")
    list_parser.add_argument("-n", "--limit", type=int, default=25, help="Maximum records to display (default: 25)")

    # --- Subcommand: delete ---
    del_parser = subparsers.add_parser("delete", help="Delete a transaction by ID")
    del_parser.add_argument("--id", type=str, required=True, help="Transaction ID to delete")

    # --- Subcommand: budget ---
    budget_parser = subparsers.add_parser("budget", help="Manage category spending budgets")
    budget_sub = budget_parser.add_subparsers(dest="budget_action", help="Budget actions")
    
    b_set = budget_sub.add_parser("set", help="Set monthly budget limit")
    b_set.add_argument("-c", "--category", type=str, required=True, help="Target category")
    b_set.add_argument("-l", "--limit", type=float, required=True, help="Monthly limit amount")
    b_set.add_argument("-w", "--warning", type=float, default=0.80, help="Warning threshold (0.1 to 1.0, default 0.8)")

    b_status = budget_sub.add_parser("status", help="Check spending against configured budgets")
    b_status.add_argument("-m", "--month", type=int, default=None, help="Month number (1-12)")
    b_status.add_argument("-y", "--year", type=int, default=None, help="Year (e.g. 2026)")

    # --- Subcommand: account ---
    acc_parser = subparsers.add_parser("account", help="Manage accounts and view balances")
    acc_sub = acc_parser.add_subparsers(dest="account_action", help="Account actions")
    acc_add = acc_sub.add_parser("add", help="Create new account")
    acc_add.add_argument("-n", "--name", type=str, required=True, help="Account name")
    acc_add.add_argument("-t", "--type", choices=["SAVINGS", "CHECKING", "CASH", "CREDIT_CARD", "INVESTMENT"], default="SAVINGS", help="Account type")
    acc_add.add_argument("-b", "--balance", type=float, default=0.0, help="Initial opening balance")
    acc_balances = acc_sub.add_parser("balance", help="Display all account balances")

    # --- Subcommand: analytics ---
    ana_parser = subparsers.add_parser("analytics", help="Generate analytics and visual breakdown")
    ana_sub = ana_parser.add_subparsers(dest="analytics_action", help="Analytics views")
    ana_sub.add_parser("overview", help="High-level lifetime financial summary")
    ana_sub.add_parser("breakdown", help="Category-wise expenditure distribution and ASCII chart")
    ana_sub.add_parser("trends", help="Month-over-month income and expense trends")

    # --- Subcommand: report ---
    rep_parser = subparsers.add_parser("report", help="Generate and print comprehensive report")
    rep_parser.add_argument("-o", "--output", type=str, default=None, help="Optional text file path to write report to")

    # --- Subcommand: export ---
    exp_csv = subparsers.add_parser("export", help="Export transaction database to CSV")
    exp_csv.add_argument("-o", "--output", type=str, required=True, help="Destination CSV file path")

    # --- Subcommand: import ---
    imp_csv = subparsers.add_parser("import", help="Import transactions from CSV file")
    imp_csv.add_argument("-i", "--input", type=str, required=True, help="Source CSV file path to import")

    return parser


def execute_cli(args: argparse.Namespace, engine: FinanceEngine) -> int:
    """Executes the parsed command and displays formatted terminal output."""
    cmd = args.command

    try:
        if cmd == "init":
            if args.reset:
                engine.repository.save_data(engine.repository.DEFAULT_DATA)
                engine.load_from_storage()
                print("[OK] Database reset to initial blank state.")
            else:
                print(f"[OK] Database initialized at: {engine.repository.file_path}")
            return 0

        elif cmd == "add-expense":
            res = engine.add_expense(
                amount=args.amount,
                category=args.category,
                date_val=args.date,
                description=args.desc,
                account=args.account,
                tags=args.tags
            )
            tx = res["transaction"]
            print(f"[OK] Expense recorded successfully! ID: {tx.id}")
            print(f"     Amount: {TerminalFormatter.format_currency(tx.amount)} | Category: {tx.category} | Date: {tx.date}")
            if res["warning"]:
                print(f"\n[ALERT] {res['warning']}")
            return 0

        elif cmd == "add-income":
            tx = engine.add_income(
                amount=args.amount,
                category=args.category,
                date_val=args.date,
                description=args.desc,
                account=args.account,
                tags=args.tags
            )
            print(f"[OK] Income recorded successfully! ID: {tx.id}")
            print(f"     Amount: {TerminalFormatter.format_currency(tx.amount)} | Category: {tx.category} | Date: {tx.date}")
            return 0

        elif cmd == "list":
            txs = engine.list_transactions(
                category=args.category,
                tx_type=args.type,
                account=args.account,
                search_query=args.search
            )
            display_txs = txs[:args.limit]
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
                for tx in display_txs
            ]
            alignments = ["left", "center", "center", "left", "right", "left", "left"]
            print(TerminalFormatter.render_table(headers, rows, alignments))
            print(f"\nShowing {len(display_txs)} of {len(txs)} matching records.")
            return 0

        elif cmd == "delete":
            removed = engine.delete_transaction(args.id)
            print(f"[OK] Removed transaction {removed.id} ({removed.category}, {TerminalFormatter.format_currency(removed.amount)}).")
            return 0

        elif cmd == "budget":
            if args.budget_action == "set":
                b = engine.set_budget(args.category, args.limit, args.warning)
                print(f"[OK] Monthly budget for '{b.category}' set to {TerminalFormatter.format_currency(b.limit_amount)} (Alert at {int(b.warning_threshold * 100)}%).")
                return 0
            else:
                evals = engine.evaluate_all_budgets(month=getattr(args, "month", None), year=getattr(args, "year", None))
                if not evals:
                    print("No budgets configured yet. Use 'fintrack budget set -c <Category> -l <Amount>' to add one.")
                    return 0
                headers = ["Category", "Monthly Limit", "Spent", "Remaining", "Used %", "Status"]
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
                alignments = ["left", "right", "right", "right", "right", "center"]
                print(TerminalFormatter.render_table(headers, rows, alignments))
                return 0

        elif cmd == "account":
            if args.account_action == "add":
                acc = engine.create_account(args.name, args.type, args.balance)
                print(f"[OK] Account '{acc.name}' ({acc.account_type}) registered with opening balance {TerminalFormatter.format_currency(acc.initial_balance)}.")
                return 0
            else:
                balances = engine.get_all_balances()
                headers = ["Account Name", "Type", "Initial Balance", "Current Balance"]
                rows = [
                    [
                        info["name"],
                        info["type"],
                        TerminalFormatter.format_currency(info["initial_balance"]),
                        TerminalFormatter.format_currency(info["current_balance"])
                    ]
                    for info in balances.values()
                ]
                alignments = ["left", "center", "right", "right"]
                print(TerminalFormatter.render_table(headers, rows, alignments))
                total_val = sum(info["current_balance"] for info in balances.values())
                print(f"\nNet Portfolio Worth Across Accounts: {TerminalFormatter.format_currency(total_val)}")
                return 0

        elif cmd == "analytics":
            reporter = FinancialReporter(list(engine._transactions.values()))
            action = args.analytics_action or "overview"

            if action == "overview":
                stats = reporter.calculate_overview()
                print("\n=== FINANCIAL OVERVIEW ===")
                print(f"Total Transactions: {stats['transaction_count']}")
                print(f"Total Income:       {TerminalFormatter.format_currency(stats['total_income'])}")
                print(f"Total Expenses:     {TerminalFormatter.format_currency(stats['total_expense'])}")
                print(f"Net Savings:        {TerminalFormatter.format_currency(stats['net_savings'])}")
                print(f"Savings Rate:       {stats['savings_rate_pct']}%")
                return 0

            elif action == "breakdown":
                breakdown = reporter.get_category_breakdown("EXPENSE")
                if not breakdown:
                    print("No expense records available to analyze.")
                    return 0
                headers = ["Category", "Expenditure", "Share %"]
                rows = [
                    [item["category"], TerminalFormatter.format_currency(item["amount"]), f"{item['percentage']}%"]
                    for item in breakdown
                ]
                print(TerminalFormatter.render_table(headers, rows, ["left", "right", "right"]))
                chart_items = [(b["category"], b["amount"]) for b in breakdown[:7]]
                print(reporter.generate_ascii_bar_chart("EXPENSE DISTRIBUTION", chart_items))
                return 0

            elif action == "trends":
                trends = reporter.get_monthly_trends()
                if not trends:
                    print("No monthly transactions recorded yet.")
                    return 0
                headers = ["Period", "Income", "Expense", "Net Cashflow", "Savings %"]
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
                return 0

        elif cmd == "report":
            reporter = FinancialReporter(list(engine._transactions.values()))
            rep_text = reporter.generate_full_text_report()
            print(rep_text)
            if args.output:
                out_path = Path(args.output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(rep_text)
                print(f"\n[OK] Report successfully saved to: {out_path.resolve()}")
            return 0

        elif cmd == "export":
            count = engine.export_to_csv(args.output)
            print(f"[OK] Exported {count} transactions to CSV file: {args.output}")
            return 0

        elif cmd == "import":
            res = engine.import_from_csv(args.input)
            print(f"[OK] CSV Import Complete!")
            print(f"     Parsed Rows:        {res['total_parsed']}")
            print(f"     Successfully Added: {res['imported']}")
            print(f"     Duplicates Skipped: {res['duplicates_skipped']}")
            if res["errors"]:
                print(f"     Failed Rows:        {len(res['errors'])}")
                for err in res["errors"][:5]:
                    print(f"     - Line {err['row']}: {err['error']}")
            return 0

        else:
            print("Please specify a valid subcommand or use --interactive / -h.")
            return 1

    except FinTrackError as fe:
        print(f"\n[ERROR] {fe}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"\n[UNEXPECTED ERROR] {exc}", file=sys.stderr)
        return 2
