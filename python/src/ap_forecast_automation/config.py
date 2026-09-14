"""Settings, loaded from environment variables (see .env.example).

Every path that used to be hardcoded in the original script lives here
instead, so the same code runs on any machine by just supplying a
`.env` file - no source edits required.
"""
########## Step 1: All imports grouped at the top ##########
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv


########## Step 2: Load the .env file FIRST, before reading any environment variable ##########
### This must happen before any os.getenv() / os.environ.get() call below,
### otherwise DATA_ROOT and every other variable will read as None
load_dotenv()


########## Step 3: Shared helper for required environment variables with a clear error message ##########
def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            f"Copy .env.example to .env and fill it in."
        )
    return value


########## Step 4: Root folder differs per machine, loaded from .env ##########
DATA_ROOT = _env("DATA_ROOT")


########## Step 5: Folder structure below DATA_ROOT is identical across machines - build once, reuse everywhere ##########
FINANCE_STATEMENTS_DIR_ACME = os.path.join(
    DATA_ROOT, "Finance", "01.Download_Acme_Statement", "03.Files"
)

FINANCE_STATEMENTS_DIR_NORTHWIND = os.path.join(
    DATA_ROOT, "Finance", "02.Download_Northwind_Statement", "03.Files"
)

FINANCE_AP_FORECAST_OUTPUT_DIR = os.path.join(
    DATA_ROOT, "Finance", "03.OutstandingAP"
)


########## Step 6: Settings dataclass, updated to match the per-supplier split ##########
@dataclass(frozen=True)
class FinanceSettings:
    statements_dir_acme: str = field(default_factory=lambda: FINANCE_STATEMENTS_DIR_ACME)
    statements_dir_northwind: str = field(default_factory=lambda: FINANCE_STATEMENTS_DIR_NORTHWIND)
    ap_forecast_output_dir: str = field(default_factory=lambda: FINANCE_AP_FORECAST_OUTPUT_DIR)


########## Step 7: Company-wide store-to-bank mapping - shared by every supplier, not supplier-specific ##########
@dataclass(frozen=True)
class StoreBankColumn:
    store_code: str
    bank_name: str


# Order matches the fixed column layout the finance team expects in every weekly report.
# Some store codes appear more than once (e.g. STORE-02, STORE-24) because that store pays
# through more than one bank account depending on the supplier.
#
# NOTE: this is synthetic sample data for the public/portfolio version of this project -
# store codes and bank names are placeholders, not real accounts.
STORE_BANK_COLUMNS: list[StoreBankColumn] = [
    StoreBankColumn(store_code="STORE-01", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-01", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-02", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-02", bank_name="Bank-3"),
    StoreBankColumn(store_code="STORE-02", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-03", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-04", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-05", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-05", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-06", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-06", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-07", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-08", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-09", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-10", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-11", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-12", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-13", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-13", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-14", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-15", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-16", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-16", bank_name="Bank-3"),
    StoreBankColumn(store_code="STORE-17", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-18", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-18", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-19", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-20", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-21", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-22", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-23", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-24", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-24", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-24", bank_name="Bank-3"),
    StoreBankColumn(store_code="STORE-25", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-26", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-27", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-28", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-29", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-29", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-30", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-31", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-32", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-33", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-33", bank_name="Bank-3"),
    StoreBankColumn(store_code="STORE-33", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-34", bank_name="Bank-2"),
    StoreBankColumn(store_code="STORE-35", bank_name="Bank-1"),
    StoreBankColumn(store_code="STORE-35", bank_name="Bank-3"),
]
