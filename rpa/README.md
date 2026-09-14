# RPA: Statement Download

The first stage of the [ap-forecast-pipeline](../README.md) case study:
a UiPath automation that logs into the company's own invoice system —
a single, store-divided system, not a supplier-hosted portal — and
downloads each store's newest statement, unattended, on a schedule.

> These are the real `.xaml` workflow files (UiPath's project format is
> plain XML, meant to be source-controlled), sanitized the same way as
> the rest of this repo — see [../SANITIZATION.md](../SANITIZATION.md).
> Design-time caches, local debug settings, and embedded screenshots
> from UiPath Studio were left out; they're local tooling artifacts, not
> source.

## Business problem

Supplier statements were only available by logging into the company's
own invoice system and working through it store by store, by hand, once
a week, downloading the newest statement for each store one at a time —
before anyone could even start building the AP forecast. That's pure
clicking, not judgment, and it had to happen on a fixed schedule for the
downstream forecast to go out on time.

## Why RPA (and not an API integration)

The invoice system is a web app behind an SSO login with no public
API available at this account's tier. Given that constraint, the
realistic options were: do it by hand every week, or automate the
browser. UI automation is the correct tool when there's no API to call —
it's not the first choice when one exists, but it's the right one here.

## Structure

- **`acme-statement-download/`** — the main UiPath project. `Main.xaml`
  orchestrates the run; `SendNewestStatements-Acme.xaml` logs into the
  invoice system and downloads the newest statement per store for the
  sample "Acme" supplier.
- **`northwind-statement-download/`** — a second, newer UiPath project
  for the sample "Northwind" supplier, following the same pattern.

Both write downloaded PDFs into a shared data folder using a fixed
filename convention, `{date}_{supplier}_{store}.pdf`, which is the
integration contract the [`python/`](../python/README.md) stage relies
on to know which file belongs to which store.

## Key design decisions

- **Selector strategy**: UI elements are targeted with UiPath's fuzzy
  selectors (`FuzzySelectorArgument`) plus an image-based fallback
  (`SearchSteps="FuzzySelector, Image"`), so small changes to the
  invoice system's DOM don't immediately break the automation.
- **Dynamic selector for store switching**: the invoice system's URL
  doesn't carry a store parameter, so there's no way to jump straight to
  a given store's data by navigating to a URL. Switching stores happens
  through the company-wide dashboard instead, using a selector built at
  runtime with the current store name substituted in — one dynamic
  selector handles every store, rather than one hardcoded selector per
  store.
- **File selection**: in the invoice system, the real statement and its
  "Account Activity Listing" are listed under the same name, so there's
  no way to tell them apart before clicking download — the robot can end
  up downloading either one. Statement files and Activity Listing files
  do download with different filename patterns, though, so after
  downloading, an if/else step checks the downloaded file's name against
  the expected Statement pattern. If it got the Activity Listing by
  mistake, it deletes that file and re-selects/downloads the real
  statement instead.
- **Error handling**: the file-selection-and-save step for each store
  runs inside a `TryCatch`. On any exception, the `Catch` block appends
  one row (store name, supplier, error message) to an in-memory Error
  data table and the loop moves on to the next store, so one store's
  failure doesn't block every other store's statement from being
  downloaded that week.
- **Exception visibility**: the Error data table is only emailed out
  once, as one summary, after every store in the run has been processed
  — not per-store as each failure happens. That keeps the RPA admin's
  inbox to one email per run (which stores failed and why) instead of a
  flood of one-off failure emails, or errors silently getting buried in
  a log file no one checks.
- **Credentials**: none are hardcoded in the workflow — this project
  followed UiPath's own best practice of keeping the invoice system
  login out of the `.xaml` files entirely (there's a `Type Into` for the account
  email, but the password step uses a separate secure-credential
  activity, so nothing sensitive lives in source control).

## What a stranger can't see from the `.xaml` alone

UiPath Studio is required to open and visually step through these
workflows — the raw XML shows the logic but not the running UI. A flow
diagram of the activity sequence and exception handling helps close
that gap (see the [top-level architecture diagram](../README.md#the-pipeline)
for how this stage fits into the full pipeline).

There's no screen recording or GIF of the automation running, and there
won't be one: everything visible on screen during a real run — the
invoice system UI, store names, statement contents — is sensitive, and
unlike text it isn't practical to mock or redact in a video.
