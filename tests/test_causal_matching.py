import numpy as np
import pandas as pd

from src.causal import nearest_neighbour_match, estimate_propensity_scores


def _sample_for_matching(n=100, seed=7):
    rng = np.random.default_rng(seed)
    age = rng.integers(20, 65, size=n)
    sex = rng.choice(["M", "F"], size=n)
    chronic = rng.integers(0, 2, size=n)
    return pd.DataFrame({"age": age, "sex": sex, "chronic_condition": chronic})


def test_nearest_neighbour_match_returns_paired_rows():
    df = _sample_for_matching()
    df["propensity_score"] = estimate_propensity_scores(
        df, "chronic_condition", ["age", "sex"]
    )
    matched = nearest_neighbour_match(
        df.dropna(subset=["propensity_score"]),
        propensity_col="propensity_score",
        treatment_col="chronic_condition",
    )
    # Equal numbers of matched treated and matched control rows.
    n_treated_matched = (matched["chronic_condition"] == 1).sum()
    n_control_matched = (matched["chronic_condition"] == 0).sum()
    assert n_treated_matched == n_control_matched
    assert n_treated_matched > 0
    # No control unit should be reused across matches.
    control_rows = matched[matched["chronic_condition"] == 0]
    assert control_rows.index.is_unique


def test_nearest_neighbour_match_no_helper_column_leaks_into_output():
    df = _sample_for_matching()
    df["propensity_score"] = estimate_propensity_scores(
        df, "chronic_condition", ["age", "sex"]
    )
    matched = nearest_neighbour_match(
        df.dropna(subset=["propensity_score"]),
        propensity_col="propensity_score",
        treatment_col="chronic_condition",
    )
    assert "_logit_propensity" not in matched.columns


def test_nearest_neighbour_match_invalid_caliper_scale_raises():
    df = pd.DataFrame({
        "propensity_score": [0.1, 0.2, 0.8, 0.9],
        "treatment": [0, 0, 1, 1],
    })
    try:
        nearest_neighbour_match(df, "propensity_score", "treatment",
                                 caliper_scale="not_a_real_scale")
        assert False, "expected a ValueError"
    except ValueError:
        pass


def test_nearest_neighbour_match_probability_scale_runs():
    """caliper_scale='probability' matches on the raw propensity score
    rather than logit(propensity score) - a separate code path from the
    default 'logit_sd' scale, and one deliberately kept available per
    decisions_log.md even though 'logit_sd' is the recommended default."""
    df = pd.DataFrame({
        "propensity_score": [0.10, 0.15, 0.55, 0.60],
        "treatment": [0, 0, 1, 1],
    })
    matched = nearest_neighbour_match(
        df, "propensity_score", "treatment",
        caliper=0.5, caliper_scale="probability",
    )
    n_treated_matched = (matched["treatment"] == 1).sum()
    n_control_matched = (matched["treatment"] == 0).sum()
    assert n_treated_matched == n_control_matched
    assert n_treated_matched > 0


def test_nearest_neighbour_match_skips_treated_unit_once_controls_exhausted():
    """With more treated units than controls, at least one treated unit
    should end up unmatched (exercises the 'no controls left' branch)
    rather than the function raising or reusing a control."""
    df = pd.DataFrame({
        "propensity_score": [0.50, 0.10, 0.90, 0.95],
        "treatment": [0, 1, 1, 1],  # 1 control, 3 treated
    })
    matched = nearest_neighbour_match(df, "propensity_score", "treatment", caliper=50.0)
    n_treated_matched = (matched["treatment"] == 1).sum()
    n_control_matched = (matched["treatment"] == 0).sum()
    # Only one control available, so at most one treated unit can be matched,
    # even with an enormous caliper that would otherwise accept every pair.
    assert n_control_matched == 1
    assert n_treated_matched == 1


def test_nearest_neighbour_match_tighter_caliper_matches_fewer_or_equal_pairs():
    df = pd.DataFrame({
        "propensity_score": [0.10, 0.30, 0.55, 0.95],
        "treatment": [0, 0, 1, 1],
    })
    loose = nearest_neighbour_match(df, "propensity_score", "treatment",
                                     caliper=5.0, caliper_scale="logit_sd")
    tight = nearest_neighbour_match(df, "propensity_score", "treatment",
                                     caliper=0.001, caliper_scale="logit_sd")
    n_loose = (loose["treatment"] == 1).sum()
    n_tight = (tight["treatment"] == 1).sum()
    assert n_tight <= n_loose
