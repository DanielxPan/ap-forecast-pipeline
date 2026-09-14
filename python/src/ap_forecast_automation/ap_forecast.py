"""Extract outstanding-balance statements from supplier PDFs into an
accounts-payable forecast workbook.

Refactored from the original script (recovered from a PDF export). The
original duplicated an entire ~90-line block per supplier; that block
is now one function, ``parse_statements_for_supplier``, parameterized
per supplier by how many characters of the filename its code occupies.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

import pandas as pd
import pdfplumber

from ap_forecast_automation.config import FinanceSettings, StoreBankColumn


START_WORDS = [
    "Balance Overdue Due by: Due by: Due by: Due on/after:",
    "Balance Overdue Due by: Due by: Due by:",
    "Balance Overdue",
]
STOP_WORDS = "Date Reference Description Due Debit Credit Balance"

# Filenames look like "{today}_{supplier_code}_{store}.pdf" - the supplier
# code length varies per supplier, so it's supplied per config below.
FILENAME_PREFIX_LEN = 11  # len("YYYY-MM-DD_")


########## Supplier configuration - bank_name removed, that's now company-wide (see config.STORE_BANK_COLUMNS) ##########
@dataclass(frozen=True)
class SupplierStatementConfig:
    key: str  # matches the supplier code embedded in the filename
    code_length: int
    sheet_name: str


def _parse_statement_page(file_path: str) -> dict:
    """Extract the item/date/amount rows from the first page of one statement."""
    with pdfplumber.open(file_path) as pdf:
        text = pdf.pages[0].extract_text()

    lines = text.split("\n")
    start_index = next((i for i, line in enumerate(lines) if any(w in line for w in START_WORDS)), None)
    end_index = next((i for i, line in enumerate(lines) if STOP_WORDS in line), None)
    lines_filtered = lines[start_index:end_index]

    headers = re.findall(r"Due by:|Due on/after:|[^\s]+", lines_filtered[0])
    dates = lines_filtered[1].split()
    dates.insert(1, dates[0])
    values = re.split(r"\s+", lines_filtered[2])

    return {"Item": headers, "Date": dates, "Amt": values}


def parse_statements_for_supplier(
    statements_dir: str, today_str: str, config: SupplierStatementConfig
) -> pd.DataFrame:
    """Parse every statement PDF for one supplier, received today, into a dataframe."""
    file_keyword = f"{today_str}_{config.key}"
    supplier_start = FILENAME_PREFIX_LEN
    supplier_end = supplier_start + config.code_length
    store_start = supplier_end + 1

    frames = []
    for file_name in os.listdir(statements_dir):
        if file_keyword not in file_name or not file_name.endswith(".pdf"):
            continue

        store = file_name[store_start:-4]
        data = _parse_statement_page(os.path.join(statements_dir, file_name))
        df = pd.DataFrame(data)
        df["Store"] = store
        df["Supplier"] = file_name[supplier_start:supplier_end]
        frames.append(df)

    if not frames:
        return pd.DataFrame(columns=["Item", "Date", "Amt", "Store", "Supplier"])
    return pd.concat(frames, ignore_index=True)


def process_statement_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize date/amount types and collapse due-date variants into one label."""
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y").dt.date
    df["Amt"] = df["Amt"].str.replace(",", "").astype(float)
    df.loc[df["Item"] == "Due on/after:", "Item"] = "Due by:"
    return df


########## No duplicate store codes appear within a single supplier's raw data, ##########
########## so pivot_table's default behaviour (no aggfunc needed) is safe here. ##########
def pivot_statement_df(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to one row per (item, date) and one column per store, with an Actual total.

    Column order is Date, Actual, Item, Supplier, then one column per store -
    Actual (the row total) sits right after Date to match the reference report
    layout, rather than trailing at the end.
    """
    pvt = df.pivot_table(index=["Item", "Date", "Supplier"], values="Amt", columns="Store")
    pvt = pvt.reset_index().sort_values(by="Date").fillna(0)

    store_columns = pvt.columns.tolist()[3:]
    pvt["Actual"] = pvt[store_columns].sum(axis=1)

    ##### Step: reorder columns to Date, Actual, Item, Supplier, then each store #####
    pvt = pvt[["Date", "Actual", "Item", "Supplier"] + store_columns]
    return pvt


########## Add the sub-header row and reindex to the full standard column layout - REWRITTEN ##########
def add_bank_details_row(
    df_pivot: pd.DataFrame, store_bank_columns: list[StoreBankColumn]
) -> pd.DataFrame:
    """Prepend the "Balance / Funds (<600) / bank" sub-header row, insert the
    Bank-1 Avail column, then reindex columns to the full standard layout.

    The sub-header row's bank labels are built from the FULL store_bank_columns
    reference table, not from whichever stores this supplier actually paid this
    week - the bank-code label is a fixed, company-wide structural fact and must
    always show correctly for all 51 columns. Only the actual transaction data
    below it should be blank for stores/banks this supplier didn't use this week.
    """
    ##### Step: every store present in this pivot is paid via Bank-1 - rename columns to match #####
    present_store_columns = df_pivot.columns.tolist()[4:]  # everything after Date/Actual/Item/Supplier
    rename_map = {store: f"{store}-Bank-1" for store in present_store_columns}
    df_renamed = df_pivot.rename(columns=rename_map)

    ##### Step: insert the new Bank-1 Avail column right after Supplier - blank for real data rows #####
    df_renamed.insert(4, "Bank-1 Avail", "")

    ##### Step: build the full standard column layout #####
    fixed_columns = ["Date", "Actual", "Item", "Supplier", "Bank-1 Avail"]
    full_store_columns = [f"{c.store_code}-{c.bank_name}" for c in store_bank_columns]

    ##### Step: build the sub-header row from the FULL reference table, always correct regardless of presence #####
    sub_header_row = ["", "Balance", "", "", "Funds (<600)"] + [c.bank_name for c in store_bank_columns]
    df_sub_header = pd.DataFrame([sub_header_row], columns=fixed_columns + full_store_columns)

    ##### Step: reindex the DATA rows to the full layout - only the data itself goes blank for unused combos #####
    df_data_reindexed = df_renamed.reindex(columns=fixed_columns + full_store_columns, fill_value="")

    return pd.concat([df_sub_header, df_data_reindexed], ignore_index=True)


########## Run the full per-supplier pipeline - UPDATED signature ##########
def build_supplier_forecast(
    statements_dir: str,
    today_str: str,
    config: SupplierStatementConfig,
    store_bank_columns: list[StoreBankColumn],
) -> pd.DataFrame:
    """Run the full per-supplier pipeline: parse -> process -> pivot -> bank row."""
    df_raw = parse_statements_for_supplier(statements_dir, today_str, config)
    df_processed = process_statement_df(df_raw)
    df_pivot = pivot_statement_df(df_processed)
    return add_bank_details_row(df_pivot, store_bank_columns)


def write_forecast_workbook(sheets: dict[str, pd.DataFrame], output_path: str) -> None:
    """Write one sheet per supplier with a uniform column width and thousands-separated numbers.

    Store columns are internally named "STORE-BANK" (e.g. "STORE-01-Bank-1") so pandas
    can tell duplicate store codes apart, but the header row shown to the
    finance team should only display the plain store code - the bank code
    already lives in the sub-header row directly underneath.
    """
    ##### Step: text columns never get thousands formatting - everything else (Actual + every store column) does #####
    TEXT_COLUMNS = {"Date", "Item", "Supplier", "Bank-1 Avail"}

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        integer_format = workbook.add_format({"num_format": "#,##0"})
        border_format = workbook.add_format({"border": 1})

        for sheet_name, df in sheets.items():
            ##### Step: build display-only headers - strip "-BANK" from store columns #####
            display_columns = [
                col if col in TEXT_COLUMNS else col.split("-")[0] for col in df.columns
            ]
            display_df = df.copy()
            display_df.columns = display_columns

            display_df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)
            sheet = writer.sheets[sheet_name]
            rows, cols = display_df.shape

            sheet.conditional_format(0, 0, rows, cols - 1, {"type": "no_errors", "format": border_format})

            ##### Step: compute one uniform column width wide enough for the longest header/value anywhere #####
            def _display_width(value):
                if isinstance(value, (int, float)):
                    try:
                        return len(f"{int(value):,}")
                    except (ValueError, TypeError):
                        return len(str(value))
                return len(str(value))

            max_content_length = max(
                (_display_width(col) for col in display_df.columns),
                default=0,
            )
            for column in display_df.columns:
                column_max = max((_display_width(v) for v in display_df[column]), default=0)
                max_content_length = max(max_content_length, column_max)
            uniform_width = max_content_length + 2

            ##### Step: apply width AND number format together in one call per column - #####
            ### calling set_column twice (once for format, once for width) would let whichever
            ### call happens last silently wipe out the format from the earlier call
            for col_num, original_column_name in enumerate(df.columns):
                column_format = None if original_column_name in TEXT_COLUMNS else integer_format
                sheet.set_column(col_num, col_num, uniform_width, column_format)


########## Entry point - loops over each supplier, one folder each - UPDATED ##########
def run(
    settings: FinanceSettings,
    supplier_configs: list[SupplierStatementConfig],
    store_bank_columns: list[StoreBankColumn],
) -> str:
    """Build the AP forecast workbook for all configured suppliers."""
    # today_str = '2026-09-10'  ### For test
    today_str = str(pd.Timestamp.today().date())

    ##### Step: each supplier reads from its own folder, looked up by key #####
    statements_dir_by_key = {
        "ACME": settings.statements_dir_acme,
        "NWIND": settings.statements_dir_northwind,
    }

    ##### Step: loop once per supplier #####
    sheets = {
        config.sheet_name: build_supplier_forecast(
            statements_dir_by_key[config.key], today_str, config, store_bank_columns
        )
        for config in supplier_configs
    }

    output_path = os.path.join(settings.ap_forecast_output_dir, f"{today_str}_AP_Forecast.xlsx")
    write_forecast_workbook(sheets, output_path)
    return output_path