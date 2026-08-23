import numpy as np
import pandas as pd

from src.panel_models import fit_fixed_effects, fixed_effects_summary_table


def _panel_sample(n_people=50, years=range(2018, 2023), seed=3):
    rng = np.random.default_rng(seed)
    rows = []
    for pid in range(n_people):
        person_effect = rng.normal(0, 5000)
        chronic_from = rng.integers(0, len(years) + 1)  # year index onset occurs (may never)
        for t, year in enumerate(years):
            chronic = 1 if t >= chronic_from else 0
            income = 50000 + person_effect - chronic * 3000 + rng.normal(0, 500)
            rows.append({"person_id": pid, "year": year, "age": 30 + t,
                         "chronic_condition": chronic, "income": income})
    return pd.DataFrame(rows)


def test_fit_fixed_effects_runs_and_recovers_negative_effect():
    df = _panel_sample()
    results = fit_fixed_effects(
        df, dependent="income", exog=["chronic_condition"],
        entity_effects=True, time_effects=False,
    )
    # The panel was constructed with a true within-person effect of
    # chronic_condition on income of -3000; the entity-FE estimate should
    # recover something in the right ballpark and the right sign.
    estimate = results.params["chronic_condition"]
    assert estimate < 0
    assert abs(estimate - (-3000)) < 800


def test_fixed_effects_summary_table_has_expected_columns():
    df = _panel_sample()
    results = fit_fixed_effects(df, dependent="income", exog=["chronic_condition"])
    summary = fixed_effects_summary_table(results)
    assert set(["coefficient", "std_error", "p_value", "ci_lower", "ci_upper"]).issubset(summary.columns)
    assert "chronic_condition" in summary.index


def test_fit_fixed_effects_without_clustering_still_runs():
    """cluster_entity=False takes a different code path (plain model.fit()
    rather than clustered SEs) - both should produce the same point
    estimate, just different standard errors."""
    df = _panel_sample()
    clustered = fit_fixed_effects(
        df, dependent="income", exog=["chronic_condition"], cluster_entity=True,
    )
    unclustered = fit_fixed_effects(
        df, dependent="income", exog=["chronic_condition"], cluster_entity=False,
    )
    assert clustered.params["chronic_condition"] == unclustered.params["chronic_condition"]


def test_fit_fixed_effects_drops_time_invariant_covariate_when_entity_effects_on():
    # age here increments in lockstep with year for every person, so once
    # both entity and time effects are included it is perfectly collinear
    # with the fixed effects and must be absorbed, not silently biased.
    df = _panel_sample()
    df["year_index"] = df["year"] - df["year"].min()
    results = fit_fixed_effects(
        df, dependent="income", exog=["chronic_condition", "age"],
        entity_effects=True, time_effects=True,
    )
    # age should have been absorbed (dropped), leaving only chronic_condition.
    assert "age" not in results.params.index
    assert "chronic_condition" in results.params.index
