"""Construction of employment-related variables."""

import pandas as pd


def add_employment_transition(df: pd.DataFrame,
                               id_col: str = "person_id",
                               year_col: str = "year",
                               employment_col: str = "employment") -> pd.DataFrame:
    """Flag year-on-year transitions into and out of employment per person."""
    df = df.sort_values([id_col, year_col]).copy()
    df["prev_employment"] = df.groupby(id_col)[employment_col].shift(1)

    df["entered_employment"] = (
        (df["prev_employment"] == 0) & (df[employment_col] == 1)
    ).astype(int)
    df["exited_employment"] = (
        (df["prev_employment"] == 1) & (df[employment_col] == 0)
    ).astype(int)
    return df


def add_prior_year_features(df: pd.DataFrame,
                             id_col: str = "person_id",
                             year_col: str = "year",
                             columns: list = None) -> pd.DataFrame:
    """Add lagged (prior-year) versions of the given columns as covariates."""
    if columns is None:
        columns = ["employment", "income"]

    df = df.sort_values([id_col, year_col]).copy()
    for col in columns:
        if col in df.columns:
            df[f"prior_{col}"] = df.groupby(id_col)[col].shift(1)
    return df
