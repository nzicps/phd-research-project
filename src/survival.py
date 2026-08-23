"""Survival analysis for business exit, built on `lifelines`.

This is the secondary/robustness estimation approach named in
docs/methodology.md, for business-survival outcomes specifically. Takes
the survival table produced by
src/entrepreneurship.compute_business_survival_with_covariates() and
fits Kaplan-Meier curves and/or a Cox proportional-hazards model.

A note on censoring (read before using on real data)
-----------------------------------------------------
`add_event_flag()` infers whether a business closure was *observed*
using a simple rule: a business whose last observed year is before the
final year of the study window is treated as having exited (event
observed); a business still recorded active in the final year is treated
as right-censored (we don't know if/when it later closed).

This is a reasonable starting assumption for administrative panel data
without an explicit exit/deregistration date, but it conflates two
different things that a real IDI/LBD analysis should try to distinguish:
1. genuine business closure, vs
2. the *person* leaving the observable population (e.g. emigrating),
   which should also be treated as censoring, not an event, even if it
   happens before the study window ends.
Confirm the right event-vs-censoring definition for your actual linked
data with your supervisors and record the decision in decisions_log.md.
"""

import pandas as pd
from lifelines import KaplanMeierFitter, CoxPHFitter


def add_event_flag(survival_df: pd.DataFrame, study_end_year: int,
                    last_observed_year_col: str = "last_observed_year",
                    event_col: str = "event_observed") -> pd.DataFrame:
    """Add a binary event/censoring indicator to a survival table.

    event_observed = 1 if the business's last observed year is before
    study_end_year (treated as an observed closure); 0 if the business
    was still recorded active in study_end_year (right-censored).

    See the module docstring for the assumption this relies on.
    """
    survival_df = survival_df.copy()
    survival_df[event_col] = (survival_df[last_observed_year_col] < study_end_year).astype(int)
    return survival_df


def fit_kaplan_meier(survival_df: pd.DataFrame,
                      duration_col: str = "survival_years",
                      event_col: str = "event_observed",
                      label: str = "Business survival") -> KaplanMeierFitter:
    """Fit a Kaplan-Meier survival curve for business survival.

    Example
    -------
    kmf = fit_kaplan_meier(survival_df)
    kmf.plot_survival_function()
    """
    kmf = KaplanMeierFitter(label=label)
    kmf.fit(durations=survival_df[duration_col], event_observed=survival_df[event_col])
    return kmf


def fit_kaplan_meier_by_group(survival_df: pd.DataFrame, group_col: str,
                               duration_col: str = "survival_years",
                               event_col: str = "event_observed") -> dict:
    """Fit a separate Kaplan-Meier curve per value of group_col (e.g.
    chronic_condition at entry), for comparing survival between groups.

    Returns a dict of {group_value: fitted KaplanMeierFitter}.
    """
    fitters = {}
    for group_value, group_df in survival_df.groupby(group_col):
        fitters[group_value] = fit_kaplan_meier(
            group_df, duration_col=duration_col, event_col=event_col,
            label=f"{group_col}={group_value}",
        )
    return fitters


def fit_cox_ph(survival_df: pd.DataFrame, covariates: list,
               duration_col: str = "survival_years",
               event_col: str = "event_observed") -> CoxPHFitter:
    """Fit a Cox proportional-hazards model of business survival on
    covariates (e.g. founder's chronic_condition, age, sex at entry).

    Rows with missing values in duration/event/covariate columns are
    dropped before fitting. Categorical covariates (e.g. "sex",
    "education") should be one-hot encoded (pd.get_dummies, drop_first)
    before calling this, the same way src/causal.estimate_propensity_scores
    handles categoricals.

    Example
    -------
    cph = fit_cox_ph(survival_df, covariates=["chronic_condition", "age"])
    cph.print_summary()
    """
    model_df = survival_df[[duration_col, event_col] + covariates].dropna()
    cph = CoxPHFitter()
    cph.fit(model_df, duration_col=duration_col, event_col=event_col)
    return cph
