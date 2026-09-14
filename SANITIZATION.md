# Sanitization Checklist

This repo is a sanitized derivative of two private repos
(`ap-forecast-automation` and `rpa-automation`). This file records
exactly what was removed or renamed, for review before making this repo
public. Neither private source repo was modified, pushed to, or had its
history touched — this repo was built from local copies with fresh git
history.

## What was removed entirely

- All UiPath design-time artifacts: `.objects/`, `.storage/`,
  `.settings/`, `.screenshots/`, `.tmh/` — local Studio caches and
  screenshots, not source, and several of the screenshots showed the
  real invoice system UI.
- All embedded `IconBase64` / `ImageBase64` / `InformativeScreenshot`
  attributes inside the `.xaml` files (design-time thumbnails).
- `MissingStatements.csv` (was empty of real data, but dropped anyway
  since it's a runtime artifact, not source).
- The unrelated `invoice-system/price-update` UiPath project from
  `rpa-automation` (a different automation, out of scope for this
  pipeline).
- `.env` (never existed in the source repo's history either —
  `.env.example` already used placeholder values).

## What was renamed / genericized

| Real value | Replaced with |
|---|---|
| Company name "[REDACTED: real company name]" | "Northstar Retail Group" |
| Windows service-account username `NorthstarBot` (in `C:\Users\NorthstarBot\...`) | `NorthstarBot` |
| Email domain `northstarretail.example.com` | `northstarretail.example.com` |
| 4 real colleague email addresses (in RPA login/notification steps) | one generic `ap-team@northstarretail.example.com` |
| Real supplier code/name #1 [REDACTED] | `ACME` / "Acme" |
| Real supplier code/name #2 [REDACTED] | `NWIND` / "Northwind" |
| Real supplier legal entity name [REDACTED] | `Northwind Distribution (Sample State) Pty Ltd (Northwind Traders)` |
| 45 real store codes [REDACTED] | `STORE-01` .. `STORE-35`, same duplicate/multi-bank structure preserved |
| Real bank names [REDACTED] — both in the config data table **and** hardcoded in `add_bank_details_row`'s column-renaming logic | `Bank-1`, `Bank-2`, `Bank-3` |
| README example bank name [REDACTED] | `Bank-1` |
| Personal dev-machine path [REDACTED] and `@author` docstring in `modify_filename.py` | generic `C:\data\...` path, author line removed |
| RPA `.xaml` filenames referencing the real supplier codes | `-Acme.xaml` / `-Northwind.xaml` |
| RPA folder names referencing the real supplier codes | `rpa/acme-statement-download` / `rpa/northwind-statement-download` |

Kept as-is (not identifying): the third-party invoice system's
product name ("Lightyear") — it's a commercial SaaS product, not
something that reveals which company uses it.

## Data

- No real statement PDFs, no real financial figures, and no notebook
  outputs are included anywhere in this repo.
- `python/scripts/generate_sample_data.py` generates synthetic statement
  PDFs (fake store/supplier codes, made-up amounts) that exercise the
  exact same parsing code path (`pdfplumber` extraction →
  `process_statement_df` → `pivot_statement_df` → `add_bank_details_row`
  → workbook export) — verified to run end-to-end with no real data.
- `python/tests/test_ap_forecast.py` was rewritten against synthetic
  values and the current function signatures (the original test file in
  the private repo had drifted out of sync with the refactored code).

## Not found / not applicable

- No internal Jira/Confluence/Notion links or ticket references were
  present in any file carried into this repo.
- No hardcoded credentials or connection strings were found in the RPA
  workflows — the invoice system's login uses a `Type Into` for the
  account email only; the password step uses a separate secure-credential activity,
  consistent with UiPath's own guidance to keep secrets in
  Orchestrator's credential store rather than in the workflow.

## Still worth doing before/after publishing

- Add a short screen recording or GIF of the RPA automation running
  (see `rpa/README.md`) — not included here, since it requires a live
  UiPath environment.
- Skim the rendered `.xaml` files once more in UiPath Studio (they're
  large; this pass was text/regex-based and was verified for
  well-formed XML and for the absence of every string above, but a
  human pass through Studio is cheap insurance before flipping this
  repo public).
