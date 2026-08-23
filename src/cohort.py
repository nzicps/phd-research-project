"""Cohort construction: define the analytical population and window."""

import pandas as pd


def build_cohort(df: pd.DataFrame, start_year: int, end_year: int,
                  id_col: str = "person_id", year_col: str = "year") -> pd.DataFrame:
    """Restrict data to the observation window and to people observed at
    least once within it.

    Parameters
    ----------
    df : pd.DataFrame
        Person-year (or similar) longitudinal data.
    start_year, end_year : int
        Inclusive observation window.
    """
    windowed = df[(df[year_col] >= start_year) & (df[year_col] <= end_year)].copy()
    return windowed


def require_balanced_panel(df: pd.DataFrame, start_year: int, end_year: int,
                            id_col: str = "person_id",
                            year_col: str = "year") -> pd.DataFrame:
    """Keep only people observed in every year of the window (a balanced panel).

    Useful for some longitudinal designs; not always the right choice —
    document the decision to use this in decisions_log.md if you do.
    """
    n_years = end_year - start_year + 1
    counts = df.groupby(id_col)[year_col].nunique()
    balanced_ids = counts[counts == n_years].index
    return df[df[id_col].isin(balanced_ids)].copy()


def cohort_summary(df: pd.DataFrame, id_col: str = "person_id",
                    year_col: str = "year") -> dict:
    """Return simple descriptive counts for a cohort dataframe."""
    return {
        "n_person_years": len(df),
        "n_unique_people": df[id_col].nunique(),
        "min_year": int(df[year_col].min()) if len(df) else None,
        "max_year": int(df[year_col].max()) if len(df) else None,
    }
