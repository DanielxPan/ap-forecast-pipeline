"""Generate synthetic supplier statement PDFs so the pipeline can be run
end-to-end without any real data.

The layout below is a minimal stand-in for a real supplier statement:
just enough text, in the right positions, for `_parse_statement_page` in
ap_forecast.py to find and extract the same "Balance / Overdue / Due by
buckets" table it looks for in a real one. Amounts and dates are made up.
"""

from __future__ import annotations

import os

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from ap_forecast_automation.config import FinanceSettings

# One statement per (supplier, store). Values are made up but internally
# consistent (the four due-by buckets sum to the Balance/Overdue total).
SAMPLE_STATEMENTS = [
    {
        "supplier_key": "ACME",
        "store": "STORE-01",
        "dates": ["01/06/2025", "08/06/2025", "15/06/2025", "22/06/2025", "29/06/2025"],
        "amounts": ["5000.00", "5000.00", "1200.00", "800.00", "1500.00", "1500.00"],
    },
    {
        "supplier_key": "ACME",
        "store": "STORE-02",
        "dates": ["01/06/2025", "08/06/2025", "15/06/2025", "22/06/2025", "29/06/2025"],
        "amounts": ["2300.00", "2300.00", "600.00", "400.00", "700.00", "600.00"],
    },
    {
        "supplier_key": "NWIND",
        "store": "STORE-01",
        "dates": ["01/06/2025", "08/06/2025", "15/06/2025", "22/06/2025", "29/06/2025"],
        "amounts": ["3100.00", "3100.00", "900.00", "500.00", "900.00", "800.00"],
    },
    {
        "supplier_key": "NWIND",
        "store": "STORE-03",
        "dates": ["01/06/2025", "08/06/2025", "15/06/2025", "22/06/2025", "29/06/2025"],
        "amounts": ["4200.00", "4200.00", "1000.00", "1000.00", "1100.00", "1100.00"],
    },
]

HEADER_LINE = "Balance Overdue Due by: Due by: Due by: Due on/after:"
STOP_LINE = "Date Reference Description Due Debit Credit Balance"


def write_statement_pdf(path: str, store: str, dates: list[str], amounts: list[str]) -> None:
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    y = height - 60

    def line(text: str) -> None:
        nonlocal y
        c.drawString(50, y, text)
        y -= 16

    line(f"Sample Supplier Statement — {store}")
    line("Statement of Account")
    line("")
    line(HEADER_LINE)
    line(" ".join(dates))
    line(" ".join(amounts))
    line("")
    line(STOP_LINE)
    line("2025-06-01  INV-1001  Sample invoice line  15/06/2025  0.00  0.00  0.00")

    c.showPage()
    c.save()


def generate(today_str: str, settings: FinanceSettings) -> list[str]:
    """Write one sample PDF per configured statement, named to match the
    "{today}_{supplier_code}_{store}.pdf" convention the parser expects.
    """
    dirs_by_supplier = {
        "ACME": settings.statements_dir_acme,
        "NWIND": settings.statements_dir_northwind,
    }

    written = []
    for stmt in SAMPLE_STATEMENTS:
        out_dir = dirs_by_supplier[stmt["supplier_key"]]
        os.makedirs(out_dir, exist_ok=True)
        filename = f"{today_str}_{stmt['supplier_key']}_{stmt['store']}.pdf"
        path = os.path.join(out_dir, filename)
        write_statement_pdf(path, stmt["store"], stmt["dates"], stmt["amounts"])
        written.append(path)
    return written


if __name__ == "__main__":
    import pandas as pd

    today_str = str(pd.Timestamp.today().date())
    paths = generate(today_str, FinanceSettings())
    print(f"Wrote {len(paths)} sample statement PDF(s):")
    for p in paths:
        print(f"  {p}")
