# FinTrack: Personal Finance & Budget Analytics CLI

## 1. Problem Statement
Managing personal finances, budgeting, and spending tracking is a ubiquitous challenge for college students, freelancers, and working professionals. Most commercial personal finance solutions either require invasive bank access permissions, mandate proprietary paid cloud subscriptions, or impose bloated graphical user interfaces that fail to cater to developers and terminal-oriented users. Furthermore, existing lightweight spreadsheets lack automated domain constraints, resulting in invalid entries, silent floating-point rounding errors, and unmonitored budget overflows.

There is a distinct need for a lightweight, privacy-focused, zero-dependency command-line personal finance and budget analytics system built in Python. Such a system must deliver robust transaction management, multi-account liquid capital tracking, category-level monthly budget threshold monitoring, detailed analytical reporting, and resilient data persistence without relying on external third-party packages.

## 2. Scope of the Project
The scope of **FinTrack** encompasses the following boundaries:
- **Core Financial Entities**: Modeling income, expenses, liquid accounts (Cash, Bank, Savings), and category-specific monthly budget caps using Object-Oriented Programming (OOP) paradigms.
- **Arithmetic Accuracy**: Utilizing Python's `decimal.Decimal` fixed-point arithmetic to guarantee financial precision and prevent IEEE 754 binary floating-point rounding errors.
- **Data Persistence**: Employing a resilient, atomic file-writing JSON storage engine backed by automatic corruption backups, alongside dual CSV import/export capabilities.
- **Spending Intelligence & Alerting**: Computing real-time budget threshold warnings (e.g., 80% warning triggers, 100% hard limit alerts) during expense logging.
- **Analytical Reporting**: Delivering statistical aggregates (Net Savings, Savings Rate percentage), category expense distributions, month-over-month trend analysis, and terminal-native ASCII data visualizations.
- **Dual Execution Interfaces**: Supporting both an interactive menu-driven terminal session for general users and a headless, non-interactive subcommand CLI interface for automated scripting and evaluation pipelines.
- **Out-of-Scope**: Direct automated bank API integration (which requires commercial API keys and network access) and GUI-heavy desktop wrappers.

## 3. Target Users
1. **University Students & Scholars**: Seeking a lightweight, private, and local utility to budget semester stipends, track living expenses, and analyze spending patterns.
2. **Software Engineers & Terminal Enthusiasts**: Developers who prefer keyboard-driven workflows, command-line automation, and headless terminal executability.
3. **Privacy-Conscious Individuals**: Users who decline to store sensitive banking credentials or financial transactions on third-party cloud servers.
4. **Academic Evaluators**: Instructors and automated test runners assessing compliance with Python software engineering principles, OOP design, validation, and testing.

## 4. High-Level Features
- **Transaction Management**: Record, categorize, tag, list, filter, search, and delete income and expense records.
- **Multi-Account Balance Tracking**: Maintain and reconcile balances across distinct liquid accounts (Bank, Physical Cash, Savings Reserves).
- **Proactive Budget Monitoring**: Configure category spending thresholds with real-time health checks (`HEALTHY`, `WARNING`, `EXCEEDED`).
- **Statistical Analytics & ASCII Charts**: Generate instant overviews of net savings, savings rate, and category-wise spending visualized through terminal ASCII horizontal bar charts.
- **Dual Data Interchange**: Seamlessly export records to standard CSV and import external CSV bank exports with row-level validation.
- **Zero-Dependency Architecture**: Runs out-of-the-box on standard Python 3.8+ across Windows, macOS, and Linux without external `pip` installations.
