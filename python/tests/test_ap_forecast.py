import pandas as pd

from ap_forecast_automation.ap_forecast import (
    add_bank_details_row,
    pivot_statement_df,
    process_statement_df,
)
from ap_forecast_automation.config import StoreBankColumn


def test_process_statement_df_normalizes_due_date_labels_and_types():
    df = pd.DataFrame(
        {
            "Item": ["Balance Overdue", "Due on/after:"],
            "Date": ["01/06/2025", "15/06/2025"],
            "Amt": ["1,234.50", "99.00"],
            "Store": ["STORE-01", "STORE-01"],
            "Supplier": ["ACME", "ACME"],
        }
    )

    result = process_statement_df(df)

    assert result["Amt"].tolist() == [1234.50, 99.00]
    assert result["Item"].tolist() == ["Balance Overdue", "Due by:"]
    assert result["Date"].iloc[0] == pd.Timestamp("2025-06-01").date()


def test_pivot_statement_df_sums_stores_into_actual_column():
    df = pd.DataFrame(
        {
            "Item": ["Balance Overdue", "Balance Overdue"],
            "Date": [pd.Timestamp("2025-06-01").date()] * 2,
            "Amt": [100.0, 50.0],
            "Store": ["STORE-01", "STORE-02"],
            "Supplier": ["ACME", "ACME"],
        }
    )

    result = pivot_statement_df(df)

    assert result["Actual"].iloc[0] == 150.0
    assert list(result.columns[:4]) == ["Date", "Actual", "Item", "Supplier"]


def test_add_bank_details_row_prepends_sub_header_and_reindexes_all_columns():
    df_pivot = pd.DataFrame(
        {
            "Date": [pd.Timestamp("2025-06-01").date()],
            "Actual": [100.0],
            "Item": ["Balance Overdue"],
            "Supplier": ["ACME"],
            "STORE-01": [100.0],
        }
    )
    store_bank_columns = [
        StoreBankColumn(store_code="STORE-01", bank_name="Bank-1"),
        StoreBankColumn(store_code="STORE-02", bank_name="Bank-2"),
    ]

    result = add_bank_details_row(df_pivot, store_bank_columns)

    # sub-header row first, then the data row
    assert len(result) == 2
    assert result.iloc[0]["Actual"] == "Balance"
    assert result.iloc[0]["STORE-01-Bank-1"] == "Bank-1"
    assert result.iloc[0]["STORE-02-Bank-2"] == "Bank-2"

    # the data row keeps its value under the renamed column, and is blank
    # for a store/bank combo this supplier didn't use this week
    assert result.iloc[1]["STORE-01-Bank-1"] == 100.0
    assert result.iloc[1]["STORE-02-Bank-2"] == ""
