"""
Terminal UI formatting, table rendering, and visual helpers.
Built using standard library without external dependencies.
"""

from typing import List, Any, Optional


class TerminalFormatter:
    """Provides formatting utilities for clean command-line presentation."""

    # Unicode & ASCII borders
    HORIZONTAL = "─"
    VERTICAL = "│"
    CORNER_TL = "┌"
    CORNER_TR = "┐"
    CORNER_BL = "└"
    CORNER_BR = "┘"
    CROSS = "┼"
    T_TOP = "┬"
    T_BOTTOM = "┴"
    T_LEFT = "├"
    T_RIGHT = "┤"

    @classmethod
    def format_currency(cls, amount: Any) -> str:
        """Formats numbers with currency symbol and thousands separator."""
        try:
            val = float(amount)
            return f"₹{val:,.2f}"
        except (ValueError, TypeError):
            return "₹0.00"

    @classmethod
    def render_table(
        cls,
        headers: List[str],
        rows: List[List[Any]],
        alignments: Optional[List[str]] = None
    ) -> str:
        """
        Renders a cleanly aligned box-drawing or ASCII table.
        Alignments can be 'left', 'right', or 'center' per column.
        """
        if not headers:
            return ""

        num_cols = len(headers)
        if alignments is None or len(alignments) != num_cols:
            alignments = ["left"] * num_cols

        # Stringify all cells
        str_headers = [str(h) for h in headers]
        str_rows = [[str(cell) for cell in row] for row in rows]

        # Calculate column widths
        col_widths = [len(h) for h in str_headers]
        for row in str_rows:
            for i in range(num_cols):
                if i < len(row):
                    col_widths[i] = max(col_widths[i], len(row[i]))

        # Helper to format a cell
        def format_cell(text: str, width: int, align: str) -> str:
            if align == "right":
                return text.rjust(width)
            elif align == "center":
                return text.center(width)
            return text.ljust(width)

        # Build table parts
        top_border = cls.CORNER_TL + cls.T_TOP.join(cls.HORIZONTAL * (w + 2) for w in col_widths) + cls.CORNER_TR
        header_row = cls.VERTICAL + cls.VERTICAL.join(f" {format_cell(str_headers[i], col_widths[i], 'center')} " for i in range(num_cols)) + cls.VERTICAL
        separator = cls.T_LEFT + cls.CROSS.join(cls.HORIZONTAL * (w + 2) for w in col_widths) + cls.T_RIGHT
        bottom_border = cls.CORNER_BL + cls.T_BOTTOM.join(cls.HORIZONTAL * (w + 2) for w in col_widths) + cls.CORNER_BR

        data_rows = []
        for row in str_rows:
            padded_cells = []
            for i in range(num_cols):
                cell_val = row[i] if i < len(row) else ""
                padded_cells.append(f" {format_cell(cell_val, col_widths[i], alignments[i])} ")
            data_rows.append(cls.VERTICAL + cls.VERTICAL.join(padded_cells) + cls.VERTICAL)

        table_lines = [top_border, header_row, separator]
        if data_rows:
            table_lines.extend(data_rows)
        else:
            empty_msg = "No records found".center(sum(col_widths) + (3 * num_cols) - 1)
            table_lines.append(f"{cls.VERTICAL}{empty_msg}{cls.VERTICAL}")
        table_lines.append(bottom_border)

        return "\n".join(table_lines)

    @classmethod
    def print_banner(cls, title: str, subtitle: str = "") -> None:
        """Prints a styled banner for terminal screens."""
        width = 66
        print("\n" + "=" * width)
        print(title.center(width))
        if subtitle:
            print(subtitle.center(width))
        print("=" * width + "\n")

    @classmethod
    def status_tag(cls, status: str) -> str:
        """Returns a formatted status tag."""
        tags = {
            "HEALTHY": "[OK] HEALTHY",
            "WARNING": "[!] WARNING",
            "EXCEEDED": "[X] EXCEEDED",
            "INCOME": "[+] INCOME",
            "EXPENSE": "[-] EXPENSE"
        }
        return tags.get(status.upper(), f"[{status}]")
