"""Basic data cleaning utilities shared across the research pipeline."""

import pandas as pd


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower-case and strip column names for consistency."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def drop_duplicate_person_years(df: pd.DataFrame,
                                 id_col: str = "person_id",
                                 year_col: str = "year") -> pd.DataFrame:
    """Drop duplicate (person, year) rows, keeping the first occurrence."""
    return df.drop_duplicates(subset=[id_col, year_col], keep="first")


def flag_missing(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Add boolean *_missing flag columns for the given columns."""
    df = df.copy()
    for col in columns:
        df[f"{col}_missing"] = df[col].isna()
    return df


def restrict_age_range(df: pd.DataFrame, min_age: int, max_age: int,
                        age_col: str = "age") -> pd.DataFrame:
    """Restrict rows to a given inclusive age range, if an age column exists."""
    if age_col not in df.columns:
        return df
    return df[(df[age_col] >= min_age) & (df[age_col] <= max_age)]
