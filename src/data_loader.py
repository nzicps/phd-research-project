"""Data access layer.

The rest of the analysis code should call `load_data(source=...)` and never
care whether the underlying data is synthetic, a local file on your
computer, or (eventually, inside the approved secure environment) IDI/LBD
data. This is the single place that should change when moving between
environments.

Supported sources
------------------
"synthetic" : the fabricated dataset from synthetic/generate_data.py
"local"     : any CSV / Excel / Parquet file on your own computer
"idi"       : IDI/LBD data, ONLY inside the approved Stats NZ secure
              environment. Raises everywhere else, deliberately.
"""

from pathlib import Path
import pandas as pd

from src.config import REPO_ROOT

DEFAULT_SYNTHETIC_PATH = REPO_ROOT / "data" / "synthetic" / "synthetic_idi_lbd.csv"

# File extensions load_local_data() knows how to read, mapped to the pandas
# reader function used for each.
_LOCAL_READERS = {
    ".csv": pd.read_csv,
    ".tsv": lambda p, **kw: pd.read_csv(p, sep="\t", **kw),
    ".xlsx": pd.read_excel,
    ".xls": pd.read_excel,
    ".parquet": pd.read_parquet,
    ".sav": None,  # SPSS — see load_local_data() docstring
    ".dta": pd.read_stata,
}


def load_data(source: str = "synthetic", path: Path = None, **kwargs) -> pd.DataFrame:
    """Load research data from the given source.

    Parameters
    ----------
    source : str
        One of "synthetic", "local", or "idi".
    path : Path, optional
        - For "synthetic": override the default synthetic data path.
        - For "local": REQUIRED — path to your file on disk.
        - For "idi": ignored.
    **kwargs
        Passed through to the underlying pandas reader (e.g. sheet_name=
        for Excel, columns= for Parquet).

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>> df = load_data("synthetic")
    >>> df = load_data("local", path="C:/Users/you/Desktop/my_export.xlsx")
    >>> df = load_data("local", path="data/raw/extract.csv", dtype={"person_id": str})
    """
    if source == "synthetic":
        return _load_synthetic_data(path)

    if source == "local":
        if path is None:
            raise ValueError(
                "source='local' requires a path, e.g. "
                "load_data('local', path='C:/Users/you/Desktop/file.csv')"
            )
        return load_local_data(path, **kwargs)

    if source == "idi":
        return _load_idi_data()

    raise ValueError(f"Unknown data source: {source!r}. Use 'synthetic', 'local', or 'idi'.")


def _load_synthetic_data(path: Path = None) -> pd.DataFrame:
    data_path = Path(path) if path else DEFAULT_SYNTHETIC_PATH

    if not data_path.exists():
        raise FileNotFoundError(
            f"Synthetic dataset not found at {data_path}.\n"
            "Run `python synthetic/generate_data.py` first to create it."
        )

    return pd.read_csv(data_path)


def load_local_data(path: Path, **kwargs) -> pd.DataFrame:
    """Load a file from your own computer, cleanly, by extension.

    Supports CSV, TSV, Excel (.xlsx/.xls), Parquet, and Stata (.dta).
    SPSS (.sav) files need `pyreadstat` — install it and this function will
    use it automatically if present.

    This function is deliberately separate from `load_data()` so it can
    also be called directly:

        from src.data_loader import load_local_data
        df = load_local_data("C:/Users/you/Desktop/export.csv")

    Parameters
    ----------
    path : str or Path
        Path to the file. Relative paths are resolved from wherever the
        notebook/script is run.
    **kwargs
        Passed through to the underlying pandas reader.
    """
    file_path = Path(path).expanduser()

    if not file_path.exists():
        raise FileNotFoundError(
            f"Could not find local file at {file_path.resolve()}.\n"
            "Check the path is correct — on Windows, forward slashes "
            "('C:/Users/you/Desktop/file.csv') work fine and avoid "
            "backslash-escaping headaches."
        )

    suffix = file_path.suffix.lower()

    if suffix == ".sav":
        try:
            import pyreadstat
        except ImportError as exc:
            raise ImportError(
                "Reading .sav (SPSS) files requires the 'pyreadstat' "
                "package. Install it with: pip install pyreadstat"
            ) from exc
        df, _meta = pyreadstat.read_sav(str(file_path), **kwargs)
        return df

    reader = _LOCAL_READERS.get(suffix)
    if reader is None:
        raise ValueError(
            f"Don't know how to read files with extension '{suffix}'. "
            f"Supported: {sorted(k for k in _LOCAL_READERS if k != '.sav')}, "
            "plus .sav (via pyreadstat)."
        )

    return reader(file_path, **kwargs)


def _load_idi_data() -> pd.DataFrame:
    """Placeholder for the IDI/LBD data access implementation.

    This function should only ever be implemented and called from inside
    the approved Stats NZ secure research environment, using whichever
    access method is confirmed with Stats NZ / University of Auckland for
    this project. It deliberately raises here so this repository can never
    accidentally be pointed at confidential data from outside that
    environment.

    WHEN YOU GET IDI ACCESS, come back to this function. The IDI research
    environment is typically SQL Server-based, so the implementation will
    likely look something like this (confirm the exact details with your
    IDI onboarding / Stats NZ documentation first):

        import pandas as pd
        import pyodbc  # or sqlalchemy, depending on what's available

        def _load_idi_data(query: str = None) -> pd.DataFrame:
            conn_str = (
                "DRIVER={SQL Server};"
                "SERVER=<confirm with Stats NZ>;"
                "DATABASE=<confirm with Stats NZ>;"
                "Trusted_Connection=yes;"
            )
            conn = pyodbc.connect(conn_str)
            query = query or "SELECT * FROM [your_approved_view]"
            return pd.read_sql(query, conn)

    Do not write real IDI table/database names into this file until you are
    working inside the approved environment — this repository (including
    its GitHub history) should never contain IDI schema/connection details.
    """
    raise NotImplementedError(
        "IDI data access must be implemented inside the approved Stats NZ "
        "secure research environment, using the access method confirmed "
        "for this project. See the docstring of this function for the "
        "likely shape of the implementation once you have access."
    )
