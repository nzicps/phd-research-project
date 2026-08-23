import numpy as np
import pandas as pd

from src.models import fit_ols, fit_logit, model_summary_table
from src.causal import estimate_propensity_scores, check_covariate_balance


def _bigger_sample(n=200, seed=1):
    rng = np.random.default_rng(seed)
    age = rng.integers(20, 65, size=n)
    sex = rng.choice(["M", "F"], size=n)
    chronic = rng.integers(0, 2, size=n)
    income = 50000 + age * 200 - chronic * 3000 + rng.normal(0, 5000, size=n)
    return pd.DataFrame({"age": age, "sex": sex, "chronic_condition": chronic,
                          "income": income})


def test_fit_ols_runs_and_has_expected_params():
    df = _bigger_sample()
    model = fit_ols(df, "income ~ chronic_condition + age + C(sex)")
    summary = model_summary_table(model)
    assert "chronic_condition" in summary.index
    assert "age" in summary.index


def test_fit_logit_runs_and_has_expected_params():
    df = _bigger_sample()
    # self_employed here is just a synthetic binary outcome for the test -
    # not meant to reflect the real synthetic generator's self_employed logic.
    rng = np.random.default_rng(2)
    df["self_employed"] = rng.integers(0, 2, size=len(df))
    model = fit_logit(df, "self_employed ~ chronic_condition + age + C(sex)")
    summary = model_summary_table(model)
    assert "chronic_condition" in summary.index
    assert "age" in summary.index


def test_estimate_propensity_scores_range():
    df = _bigger_sample()
    scores = estimate_propensity_scores(df, "chronic_condition", ["age", "sex"])
    assert scores.between(0, 1).all()
    assert len(scores) == len(df)


def test_check_covariate_balance_columns():
    df = _bigger_sample()
    balance = check_covariate_balance(df, "chronic_condition", ["age"])
    assert set(["covariate", "treated_mean", "control_mean", "smd"]).issubset(balance.columns)
