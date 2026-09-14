# AP Forecast Automation

The `python/` half of the [ap-forecast-pipeline](../README.md) case study:
an automation that turns a folder of supplier statement PDFs into a
ready-to-forward accounts-payable forecast workbook. This is the
sanitized, portfolio version of an automation originally built and run
weekly for a multi-site retail business — see the [top-level
README](../README.md) for the full story and the [`rpa/`
stage](../rpa/README.md) that feeds it.

## Business problem

Forecasting upcoming accounts-payable meant manually opening each
supplier's statement PDF, reading off the overdue balance by due-date
bucket, and retyping it into a spreadsheet — for every store, every
supplier, every week.

## What it does

`ap_forecast.py` parses each supplier's statement PDF directly with
`pdfplumber`, extracting the overdue-balance table by locating it
between known header/footer text markers, pivots it into one row per
due-date bucket with one column per store, and writes a multi-sheet
Excel workbook (one sheet per supplier) ready to forward to the finance
team. Each sheet gets one label row naming which bank the payment run
should go through per store (e.g. "Bank-1") — a routing label only,
never an account number or any other transfer detail.

## Project layout

```
src/ap_forecast_automation/
├── config.py       # settings loaded from .env — no hardcoded paths
└── ap_forecast.py  # PDF parsing + pivot + workbook export
scripts/
├── run_ap_forecast.py       # CLI entry point
└── generate_sample_data.py  # builds synthetic statement PDFs to run against
```

## Running it locally

```bash
pip install -e ".[dev]"
cp .env.example .env                        # fill in real paths for your machine
python scripts/generate_sample_data.py       # creates sample statement PDFs under $DATA_ROOT
python scripts/run_ap_forecast.py
```

This runs end-to-end against synthetic sample data (fake store codes,
supplier codes, and bank labels) — no real statements needed. Update
`SUPPLIER_CONFIGS` in `scripts/run_ap_forecast.py` with your real
supplier codes to point it at real statements instead.

## Notes on this refactor

The original script duplicated an entire ~90-line parsing block once
per supplier (copy-pasted, with only the supplier name changed). That's
now one function, `parse_statements_for_supplier`, parameterized by a
`SupplierStatementConfig` (the supplier's filename code and its length,
since that varies per supplier) — adding a new supplier means adding one
config entry, not copying 90 lines.

## About this public version

This is a sanitized derivative of a private production repository.
Company name, real store codes, real bank names, and real supplier
names have all been replaced with placeholders; sample data is
synthetic. See the top-level README for details.
