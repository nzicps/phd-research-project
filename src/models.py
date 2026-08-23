"""Regression model helpers built on statsmodels."""

import pandas as pd
import statsmodels.formula.api as smf


def fit_ols(df: pd.DataFrame, formula: str):
    """Fit an OLS model using a statsmodels formula string.

    Example
    -------
    fit_ols(df, "income ~ chronic_condition + age + C(sex) + C(education)")
    """
    model = smf.ols(formula=formula, data=df).fit()
    return model


def fit_logit(df: pd.DataFrame, formula: str):
    """Fit a logistic regression model using a statsmodels formula string.

    Example
    -------
    fit_logit(df, "self_employed ~ chronic_condition + age + C(sex)")
    """
    model = smf.logit(formula=formula, data=df).fit()
    return model


def model_summary_table(model) -> pd.DataFrame:
    """Return a tidy dataframe of coefficients, std errors, p-values, CIs."""
    summary = pd.DataFrame({
        "coefficient": model.params,
        "std_error": model.bse,
        "p_value": model.pvalues,
    })
    ci = model.conf_int()
    ci.columns = ["ci_lower", "ci_upper"]
    return summary.join(ci)
