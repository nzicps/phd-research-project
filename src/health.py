"""Construction of health-related variables.

Placeholder definitions using the synthetic dataset's column names.
Replace with actual IDI variable logic once confirmed via the data
dictionary and DataInfo+.
"""

import pandas as pd


def add_chronic_condition_onset(df: pd.DataFrame,
                                 id_col: str = "person_id",
                                 year_col: str = "year",
                                 condition_col: str = "chronic_condition") -> pd.DataFrame:
    """Flag the first year in which each person has a recorded chronic condition."""
    df = df.sort_values([id_col, year_col]).copy()
    first_onset_year = (
        df[df[condition_col] == 1]
        .groupby(id_col)[year_col]
        .min()
        .rename("chronic_onset_year")
    )
    df = df.merge(first_onset_year, on=id_col, how="left")
    df["chronic_onset_flag"] = (df[year_col] == df["chronic_onset_year"]).astype(int)
    return df


def add_condition_duration(df: pd.DataFrame,
                            id_col: str = "person_id",
                            year_col: str = "year",
                            condition_col: str = "chronic_condition") -> pd.DataFrame:
    """Add a running count of consecutive years with a chronic condition."""
    df = df.sort_values([id_col, year_col]).copy()

    def _running_duration(group):
        cond = group[condition_col].values
        duration = []
        running = 0
        for v in cond:
            running = running + 1 if v == 1 else 0
            duration.append(running)
        group = group.copy()
        group["chronic_condition_duration"] = duration
        return group

    return df.groupby(id_col, group_keys=False)[df.columns].apply(_running_duration)
