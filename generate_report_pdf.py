#!/usr/bin/env python3
"""
Report PDF / HTML Generator for FinTrack.
Converts PROJECT_REPORT.md into a styled, publication-ready HTML report with print-CSS.
Users can open the generated HTML file in any browser and use 'Print to PDF' (Ctrl+P)
to generate the exact PDF required for portal submission.
"""

import sys
import re
from pathlib import Path


def markdown_to_html(md_text: str) -> str:
    """Converts basic markdown formatting to clean HTML without external packages."""
    html_lines = []
    in_code_block = False
    in_list = False
    in_table = False
    table_headers_done = False

    lines = md_text.splitlines()

    for line in lines:
        stripped = line.strip()

        # Handle Code Blocks
        if stripped.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html_lines.append(f'<pre><code class="language-{lang}">')
                in_code_block = True
            continue

        if in_code_block:
            # Escape HTML entities inside code
            escaped = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            html_lines.append(escaped)
            continue

        # Handle Tables
        if "|" in line and stripped.startswith("|") and stripped.endswith("|"):
            parts = [p.strip() for p in stripped[1:-1].split("|")]
            if all(re.match(r"^:?-+:?$", p) for p in parts):
                # Separator line
                table_headers_done = True
                continue

            if not in_table:
                html_lines.append("<table>")
                in_table = True
                table_headers_done = False

            tag = "td" if table_headers_done else "th"
            cells = "".join(f"<{tag}>{p}</{tag}>" for p in parts)
            html_lines.append(f"<tr>{cells}</tr>")
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                table_headers_done = False

        # Close unclosed lists if line is not a list item
        if in_list and not (stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s", stripped)):
            html_lines.append("</ul>")
            in_list = False

        # Headers
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{stripped[2:]}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{stripped[3:]}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{stripped[4:]}</h3>")
        elif stripped.startswith("#### "):
            html_lines.append(f"<h4>{stripped[5:]}</h4>")
        elif stripped.startswith("---"):
            html_lines.append("<hr/>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            content = stripped[2:]
            html_lines.append(f"<li>{parse_inline(content)}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if not in_list:
                html_lines.append("<ol>")
                in_list = True
            content = re.sub(r"^\d+\.\s*", "", stripped)
            html_lines.append(f"<li>{parse_inline(content)}</li>")
        elif stripped == "":
            html_lines.append("")
        else:
            html_lines.append(f"<p>{parse_inline(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</table>")
    if in_code_block:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


def parse_inline(text: str) -> str:
    """Parses bold, italic, inline code, and links."""
    # Bold **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic *text*
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Inline code `code`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links [title](url)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def build_full_html_document(body_html: str, title: str = "Project Report") -> str:
    """Wraps body in an academic styled document with print CSS."""
    css = """
    @page {
        size: A4;
        margin: 20mm 15mm 20mm 15mm;
        @bottom-right {
            content: counter(page);
        }
    }
    body {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        color: #24292e;
        line-height: 1.6;
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
        background-color: #ffffff;
    }
    h1 {
        color: #1a365d;
        border-bottom: 2px solid #2b6cb0;
        padding-bottom: 8px;
        font-size: 26px;
        margin-top: 30px;
        text-align: center;
    }
    h2 {
        color: #2b6cb0;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 6px;
        margin-top: 28px;
        font-size: 20px;
        page-break-after: avoid;
    }
    h3 {
        color: #2d3748;
        font-size: 16px;
        margin-top: 20px;
        page-break-after: avoid;
    }
    p, li {
        font-size: 14px;
        color: #333333;
    }
    ul, ol {
        padding-left: 24px;
        margin-bottom: 12px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 16px 0;
        font-size: 13px;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #cbd5e0;
        padding: 8px 12px;
        text-align: left;
    }
    th {
        background-color: #edf2f7;
        color: #1a202c;
        font-weight: 600;
    }
    tr:nth-child(even) {
        background-color: #f7fafc;
    }
    pre {
        background-color: #f7fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 12px;
        overflow-x: auto;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 12px;
        line-height: 1.45;
        page-break-inside: avoid;
    }
    code {
        font-family: 'Consolas', 'Courier New', monospace;
        background-color: #edf2f7;
        padding: 2px 4px;
        border-radius: 4px;
        font-size: 12px;
    }
    pre code {
        background-color: transparent;
        padding: 0;
    }
    hr {
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 24px 0;
    }
    @media print {
        body {
            padding: 0;
        }
        .no-print {
            display: none;
        }
        h2 {
            page-break-before: auto;
        }
    }
    .print-banner {
        background-color: #ebf8ff;
        border: 1px solid #bee3f8;
        color: #2b6cb0;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 24px;
        font-size: 14px;
    }
    """

    banner = """
    <div class="print-banner no-print">
        <strong>Report Export Instructions:</strong> Press <code>Ctrl + P</code> (or Cmd + P on Mac) and select 
        <strong>"Save as PDF"</strong> to generate the PDF report for portal upload.
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{css}</style>
</head>
<body>
    {banner}
    {body_html}
</body>
</html>"""


def main():
    base_dir = Path(__file__).resolve().parent
    report_md_path = base_dir / "PROJECT_REPORT.md"
    output_html_path = base_dir / "PROJECT_REPORT.html"

    if not report_md_path.exists():
        print(f"Error: {report_md_path} does not exist.", file=sys.stderr)
        return 1

    with open(report_md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    html_body = markdown_to_html(md_content)
    full_html = build_full_html_document(html_body, title="FinTrack - Academic Project Report")

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)

    print(f"[OK] Generated styled HTML report at: {output_html_path}")
    print("     Open this file in your web browser and choose 'Print to PDF' (Ctrl+P) to submit the PDF report!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
