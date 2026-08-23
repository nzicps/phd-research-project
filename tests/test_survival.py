import pandas as pd

from src.survival import add_event_flag, fit_kaplan_meier, fit_kaplan_meier_by_group, fit_cox_ph
from src.entrepreneurship import compute_business_survival_with_covariates


def _survival_sample():
    return pd.DataFrame({
        "business_id": ["B1", "B2", "B3", "B4"],
        "entry_year": [2018, 2019, 2020, 2015],
        "last_observed_year": [2020, 2023, 2021, 2023],  # study ends 2023
        "survival_years": [3, 5, 2, 9],
        "chronic_condition": [1, 0, 1, 0],
        "age": [45, 30, 50, 35],
    })


def test_add_event_flag_marks_closures_and_censoring():
    survival = add_event_flag(_survival_sample(), study_end_year=2023)
    # B1 and B3 closed before the study ended -> event observed.
    # B2 and B4 were still active in the final study year -> censored.
    flags = survival.set_index("business_id")["event_observed"].to_dict()
    assert flags["B1"] == 1
    assert flags["B3"] == 1
    assert flags["B2"] == 0
    assert flags["B4"] == 0


def test_fit_kaplan_meier_runs_and_has_survival_function():
    survival = add_event_flag(_survival_sample(), study_end_year=2023)
    kmf = fit_kaplan_meier(survival)
    assert kmf.survival_function_ is not None
    assert len(kmf.survival_function_) > 0


def test_fit_kaplan_meier_by_group_returns_one_fitter_per_group():
    survival = add_event_flag(_survival_sample(), study_end_year=2023)
    fitters = fit_kaplan_meier_by_group(survival, group_col="chronic_condition")
    assert set(fitters.keys()) == {0, 1}
    for fitter in fitters.values():
        assert fitter.survival_function_ is not None


def test_fit_cox_ph_runs_and_returns_fitted_model():
    # Use a larger synthetic sample than _survival_sample() so the model
    # has enough variation to converge without warnings (the 4-row sample
    # above is fine for testing add_event_flag / KM, but too small for
    # a stable Cox fit).
    import numpy as np
    n = 60
    rand = np.random.default_rng(11)
    survival = pd.DataFrame({
        "business_id": [f"B{i}" for i in range(n)],
        "chronic_condition": rand.integers(0, 2, size=n),
        "age": rand.integers(25, 60, size=n),
        "survival_years": rand.integers(1, 9, size=n),
        "event_observed": rand.integers(0, 2, size=n),
    })
    cph = fit_cox_ph(survival, covariates=["chronic_condition", "age"])
    assert "chronic_condition" in cph.params_.index
    assert "age" in cph.params_.index


def test_compute_business_survival_with_covariates_joins_founder_covariates(sample_panel):
    from src.entrepreneurship import add_business_entry
    df = add_business_entry(sample_panel)
    survival = compute_business_survival_with_covariates(
        df, covariate_cols=["age", "sex", "chronic_condition"],
    )
    assert "person_id" in survival.columns
    assert "age" in survival.columns
    # sample_panel has one business (B0001) owned by person 2, entering 2019.
    row = survival[survival["business_id"] == "B0001"].iloc[0]
    assert row["person_id"] == 2
    assert row["age"] == 46  # person 2's age in 2019, the entry year
