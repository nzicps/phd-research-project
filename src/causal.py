"""Propensity-score and causal-inference helpers.

Starting point only — extend/replace with the specific design agreed with
supervisors (matching vs weighting, chosen estimator, etc.) and record the
decision in docs/decisions_log.md.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression


def estimate_propensity_scores(df: pd.DataFrame, treatment_col: str,
                                covariates: list) -> pd.Series:
    """Estimate propensity scores P(treatment=1 | covariates) via logistic regression.

    Rows with missing values in the treatment or covariate columns are
    dropped before fitting; the returned Series is indexed to match df.
    """
    model_df = df[[treatment_col] + covariates].dropna()

    X = pd.get_dummies(model_df[covariates], drop_first=True)
    y = model_df[treatment_col]

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X, y)

    scores = clf.predict_proba(X)[:, 1]
    return pd.Series(scores, index=model_df.index, name="propensity_score")


def _logit(p: pd.Series) -> pd.Series:
    """Logit transform, clipped away from 0/1 to avoid +/-inf."""
    p_clipped = p.clip(1e-6, 1 - 1e-6)
    return np.log(p_clipped / (1 - p_clipped))


def nearest_neighbour_match(df: pd.DataFrame, propensity_col: str,
                             treatment_col: str, caliper: float = 0.2,
                             caliper_scale: str = "logit_sd") -> pd.DataFrame:
    """Greedy 1:1 nearest-neighbour matching on propensity score.

    A simple, transparent starting implementation. For production research
    use, consider a dedicated matching package once the design is finalised.

    Parameters
    ----------
    caliper : float
        Maximum allowed distance between a treated unit and its matched
        control before the pair is discarded.
    caliper_scale : {"logit_sd", "probability"}
        How `caliper` is interpreted:
        - "logit_sd" (default, and the recommended standard practice —
          Austin, 2011): units are matched on logit(propensity score), and
          `caliper` is expressed as a multiple of the pooled standard
          deviation of the logit-transformed propensity score across the
          full sample (so `caliper=0.2` means "within 0.2 SDs").
        - "probability": units are matched on the raw propensity score
          (0-1 scale) and `caliper` is an absolute probability difference.
          NOTE: a raw-probability caliper of 0.2 is very wide (it is a
          fifth of the entire [0, 1] range) and will typically accept
          poor matches — prefer "logit_sd" unless you have a specific
          reason to match on the raw scale. Document the choice either
          way in decisions_log.md.
    """
    if caliper_scale not in {"logit_sd", "probability"}:
        raise ValueError("caliper_scale must be 'logit_sd' or 'probability'")

    df = df.copy()
    if caliper_scale == "logit_sd":
        match_col = "_logit_propensity"
        df[match_col] = _logit(df[propensity_col])
        pooled_sd = df[match_col].std()
        distance_threshold = caliper * pooled_sd if pooled_sd else 0.0
    else:
        match_col = propensity_col
        distance_threshold = caliper

    treated = df[df[treatment_col] == 1].copy()
    control = df[df[treatment_col] == 0].copy()

    matches = []
    used_control_idx = set()

    for t_idx, t_row in treated.iterrows():
        diffs = (control[match_col] - t_row[match_col]).abs()
        diffs = diffs[~control.index.isin(used_control_idx)]
        if diffs.empty:
            continue
        best_idx = diffs.idxmin()
        if diffs[best_idx] <= distance_threshold:
            matches.append((t_idx, best_idx))
            used_control_idx.add(best_idx)

    matched_treated = df.loc[[m[0] for m in matches]].drop(columns=[match_col], errors="ignore")
    matched_control = df.loc[[m[1] for m in matches]].drop(columns=[match_col], errors="ignore")
    return pd.concat([matched_treated, matched_control])


def check_covariate_balance(df: pd.DataFrame, treatment_col: str,
                             covariates: list) -> pd.DataFrame:
    """Compute standardised mean differences for covariates by treatment group.

    A common rule of thumb is that |SMD| < 0.1 indicates reasonable balance.
    """
    rows = []
    for cov in covariates:
        t_vals = df.loc[df[treatment_col] == 1, cov]
        c_vals = df.loc[df[treatment_col] == 0, cov]
        pooled_std = np.sqrt((t_vals.var() + c_vals.var()) / 2)
        smd = (t_vals.mean() - c_vals.mean()) / pooled_std if pooled_std else np.nan
        rows.append({"covariate": cov, "treated_mean": t_vals.mean(),
                      "control_mean": c_vals.mean(), "smd": smd})
    return pd.DataFrame(rows)
