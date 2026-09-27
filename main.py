#!/usr/bin/env python3
"""
FinTrack - Personal Finance & Budget Analytics CLI
Main Application Entrypoint.

Usage:
    python main.py                    # Launches the interactive terminal dashboard
    python main.py --interactive      # Interactive mode explicitly
    python main.py <command> [args]   # Direct headless CLI execution

Course: Python Essentials
"""

import sys
from fintrack.core.engine import FinanceEngine
from fintrack.cli.argument_parser import setup_cli_parser, execute_cli
from fintrack.cli.interactive import InteractiveSession


def main() -> int:
    """Main routing function for both CLI and interactive modes."""
    parser = setup_cli_parser()

    # If no arguments provided, default to interactive session
    if len(sys.argv) == 1:
        engine = FinanceEngine()
        session = InteractiveSession(engine)
        session.run()
        return 0

    args = parser.parse_args()

    engine = FinanceEngine()

    if args.interactive:
        session = InteractiveSession(engine)
        session.run()
        return 0

    if not args.command:
        parser.print_help()
        return 1

    return execute_cli(args, engine)


if __name__ == "__main__":
    sys.exit(main())
