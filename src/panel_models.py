"""Panel data models (fixed effects) built on `linearmodels`.

This is the primary longitudinal estimation approach named in
docs/methodology.md: exploiting the panel structure of IDI/LBD to track
outcomes (e.g. income) against exposures (e.g. chronic condition) while
controlling for person-level and/or time-level unobserved heterogeneity
via fixed effects, rather than relying only on the cross-sectional OLS in
src/models.py.

`src/models.fit_ols` remains useful for cross-sectional specifications
and quick diagnostics; use this module once the panel structure itself
(within-person variation over time) is what identifies the effect of
interest.
"""

import pandas as pd
from linearmodels.panel import PanelOLS


def _to_panel_index(df: pd.DataFrame, entity_col: str, time_col: str) -> pd.DataFrame:
    """Return a copy of df indexed by (entity, time), as linearmodels requires."""
    return df.set_index([entity_col, time_col])


def fit_fixed_effects(df: pd.DataFrame, dependent: str, exog: list,
                       entity_col: str = "person_id", time_col: str = "year",
                       entity_effects: bool = True, time_effects: bool = False,
                       cluster_entity: bool = True, drop_absorbed: bool = True):
    """Fit a panel fixed-effects regression: dependent ~ exog, with
    person (entity) and/or year (time) fixed effects absorbed.

    Parameters
    ----------
    df : pd.DataFrame
        Person-year (or similar) panel data, one row per (entity, time).
    dependent : str
        Name of the outcome column, e.g. "income".
    exog : list of str
        Names of the explanatory variable columns, e.g.
        ["chronic_condition", "age"]. Time-invariant covariates (e.g. sex)
        are absorbed by entity fixed effects and will be dropped
        automatically if entity_effects=True — this is expected, not a
        bug: a person-level fixed effect cannot be identified separately
        from a variable that never varies within that person.
    entity_col, time_col : str
        Columns identifying the panel's entity (e.g. person) and time
        (e.g. year) dimensions.
    entity_effects : bool
        Include person fixed effects (controls for all time-invariant
        person-level unobserved heterogeneity). Default True — this is
        usually the point of using a panel FE model over pooled OLS.
    time_effects : bool
        Include year fixed effects (controls for economy-wide/year-level
        shocks common to everyone, e.g. a recession year). Default False;
        set True if you want a two-way fixed effects model.
    cluster_entity : bool
        Cluster standard errors by entity (person). Default True — the
        standard choice for person-year panel data, since errors for the
        same person across years are very unlikely to be independent.
    drop_absorbed : bool
        Passed to PanelOLS — silently drop exog columns that are
        perfectly absorbed by the fixed effects (e.g. time-invariant
        covariates under entity_effects=True) rather than raising.

    Returns
    -------
    linearmodels.panel.results.PanelEffectsResults

    Example
    -------
    fit_fixed_effects(
        df, dependent="income", exog=["chronic_condition", "age"],
        entity_effects=True, time_effects=True,
    )
    """
    panel_df = _to_panel_index(df[[entity_col, time_col, dependent] + exog].dropna(),
                                entity_col, time_col)

    y = panel_df[dependent]
    X = panel_df[exog]

    model = PanelOLS(y, X, entity_effects=entity_effects, time_effects=time_effects,
                      drop_absorbed=drop_absorbed)

    if cluster_entity:
        return model.fit(cov_type="clustered", cluster_entity=True)
    return model.fit()


def fixed_effects_summary_table(results) -> pd.DataFrame:
    """Return a tidy dataframe of coefficients, std errors, p-values, CIs
    from a fit_fixed_effects() result — mirrors
    src/models.model_summary_table() for consistency."""
    summary = pd.DataFrame({
        "coefficient": results.params,
        "std_error": results.std_errors,
        "p_value": results.pvalues,
    })
    ci = results.conf_int()
    ci.columns = ["ci_lower", "ci_upper"]
    return summary.join(ci)
