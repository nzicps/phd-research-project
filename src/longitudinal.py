"""Longitudinal / descriptive analysis helpers."""

import pandas as pd


def yearly_summary(df: pd.DataFrame, value_col: str, year_col: str = "year",
                    agg: str = "mean") -> pd.DataFrame:
    """Summarise a value column by year (e.g. average income by year)."""
    return (
        df.groupby(year_col)[value_col]
        .agg(agg)
        .reset_index()
        .rename(columns={value_col: f"{agg}_{value_col}"})
    )


def transition_matrix(df: pd.DataFrame, state_col: str,
                       id_col: str = "person_id",
                       year_col: str = "year") -> pd.DataFrame:
    """Build a simple year-on-year state transition count matrix.

    E.g. for an employment state column with values {0, 1}, this returns
    counts of 0->0, 0->1, 1->0, 1->1 transitions across all consecutive
    person-year pairs.
    """
    df = df.sort_values([id_col, year_col]).copy()
    df["prev_state"] = df.groupby(id_col)[state_col].shift(1)
    df["prev_year"] = df.groupby(id_col)[year_col].shift(1)

    consecutive = df[df[year_col] - df["prev_year"] == 1]

    matrix = (
        consecutive.groupby(["prev_state", state_col])
        .size()
        .reset_index(name="count")
        .rename(columns={"prev_state": "from_state", state_col: "to_state"})
    )
    return matrix
