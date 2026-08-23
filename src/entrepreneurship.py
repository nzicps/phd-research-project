"""Construction of entrepreneurship / business-related variables."""

import pandas as pd


def add_business_entry(df: pd.DataFrame,
                        id_col: str = "person_id",
                        year_col: str = "year",
                        self_employed_col: str = "self_employed") -> pd.DataFrame:
    """Flag the first year a person is recorded as self-employed."""
    df = df.sort_values([id_col, year_col]).copy()
    entry_year = (
        df[df[self_employed_col] == 1]
        .groupby(id_col)[year_col]
        .min()
        .rename("business_entry_year")
    )
    df = df.merge(entry_year, on=id_col, how="left")
    df["business_entry_flag"] = (df[year_col] == df["business_entry_year"]).astype(int)
    return df


def compute_business_survival(df: pd.DataFrame,
                               business_col: str = "business_id",
                               year_col: str = "year") -> pd.DataFrame:
    """Compute a simple survival table: years active per business_id.

    Returns one row per business with entry year, last observed year, and
    a naive survival duration. This is a starting point for a proper
    survival analysis (see src/survival.py and lifelines) rather than a
    finished model.
    """
    businesses = df[df[business_col].notna()]
    survival = (
        businesses.groupby(business_col)[year_col]
        .agg(entry_year="min", last_observed_year="max")
        .reset_index()
    )
    survival["survival_years"] = (
        survival["last_observed_year"] - survival["entry_year"] + 1
    )
    return survival


def compute_business_survival_with_covariates(
        df: pd.DataFrame, covariate_cols: list,
        business_col: str = "business_id", year_col: str = "year",
        id_col: str = "person_id") -> pd.DataFrame:
    """Like compute_business_survival(), but also attaches the founder's
    covariate values (e.g. age, sex, chronic_condition) as measured in
    the business's entry year, and prepares the table for survival
    analysis in src/survival.py.

    Assumes each business_id maps to exactly one person_id (true of the
    synthetic generator; confirm this holds for the real IDI/LBD business
    linkage before relying on it — a person could plausibly found more
    than one business, which would need a different join).

    Returns one row per business with: business_col, id_col, entry_year,
    last_observed_year, survival_years, and one column per entry in
    covariate_cols (covariate value at entry_year).
    """
    survival = compute_business_survival(df, business_col=business_col, year_col=year_col)

    # One person_id per business — take the first (should be unique; see
    # docstring assumption above).
    owner = (
        df[df[business_col].notna()]
        .groupby(business_col)[id_col]
        .first()
        .rename(id_col)
    )
    survival = survival.merge(owner, on=business_col, how="left")

    # Covariates as measured in the business's own entry year.
    entry_covariates = df[[id_col, year_col] + covariate_cols].rename(
        columns={year_col: "entry_year"}
    )
    survival = survival.merge(entry_covariates, on=[id_col, "entry_year"], how="left")

    return survival
