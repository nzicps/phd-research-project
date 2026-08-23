# Importing Data Into This Repository

## From your own computer (works now)

```python
from src.data_loader import load_data

df = load_data("local", path="C:/Users/you/Desktop/my_export.xlsx")
df = load_data("local", path="data/raw/extract.csv", dtype={"person_id": str})
```

Supported formats, by file extension: `.csv`, `.tsv`, `.xlsx`, `.xls`,
`.parquet`, `.dta` (Stata), and `.sav` (SPSS — requires
`pip install pyreadstat`). Extra keyword arguments are passed straight
through to the underlying pandas reader (e.g. `sheet_name=` for Excel).

If your file uses a format not listed above, tell me the format and I'll
add a reader for it — `src/data_loader.py` is the only place that needs to
change.

**Where to put imported files:** copy them into `data/raw/` or
`data/processed/` (both are already `.gitignore`-covered so they're never
accidentally pushed to GitHub) rather than leaving them elsewhere on your
computer — that way every notebook can find them via a relative path.

## From IDI (not possible yet — and shouldn't be faked)

There is no clean way to "import from IDI" into this repository today,
and there deliberately shouldn't be one yet, for two reasons:

1. **You don't have IDI access yet.** Until Stats NZ / University of
   Auckland approve your project, there is no data to import and no
   connection details to build against.
2. **The access method is decided by Stats NZ/UoA, not by us.** IDI is
   typically accessed via a SQL Server-based secure environment (query the
   database with something like `pyodbc` or `SQLAlchemy` + `pd.read_sql`),
   but the exact server, database, and permitted packages are configured
   per-project once you're onboarded. Building a generic connector now
   would mean guessing at details that may be wrong, and — more
   importantly — writing IDI schema/connection information into files that
   could end up in this GitHub repository's history is exactly the kind of
   accidental exposure the `.gitignore` and `_load_idi_data()` stub in
   `src/data_loader.py` are designed to prevent.

**What to do instead, once you get access:**

`src/data_loader.py` already has a template in the `_load_idi_data()`
docstring showing the likely shape of the implementation (a `pyodbc`
connection + `pd.read_sql`). When you're inside the secure environment:

1. Confirm the exact connection method with your IDI onboarding
   documentation / Stats NZ.
2. Implement `_load_idi_data()` **inside the secure environment only** —
   never on your local machine, never pushed to this public/private GitHub
   repo.
3. Everything downstream — `src/cohort.py`, `src/health.py`,
   `src/causal.py`, all the notebooks — needs no changes at all, because
   they only ever call `load_data(source=...)` and don't know or care
   where the data came from. That's the entire point of this layer.

If IDI permits a limited, non-identifying code transfer mechanism (confirm
this with Stats NZ/UoA), the *code* for `_load_idi_data()` itself could
potentially be brought back out and merged into this repo for
documentation purposes — but never any data, connection strings, or
schema details that reveal IDI internals.
