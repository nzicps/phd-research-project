import pandas as pd

from src.employment import add_employment_transition, add_prior_year_features


def test_add_prior_year_features_default_columns(sample_panel):
    out = add_prior_year_features(sample_panel)

    assert "prior_employment" in out.columns
    assert "prior_income" in out.columns

    # Person 1: employment [1, 1, 0] across 2018-19-20 -> prior_employment
    # for 2019 should be person 1's 2018 value (1), and for 2020 should be
    # person 1's 2019 value (1). The first year in the panel has no prior
    # value, so it's NaN.
    person1 = out[out["person_id"] == 1].sort_values("year")
    assert pd.isna(person1["prior_employment"].iloc[0])
    assert person1["prior_employment"].iloc[1] == 1
    assert person1["prior_employment"].iloc[2] == 1

    # Same check for income: person 1's income was [60000, 58000, 0].
    assert pd.isna(person1["prior_income"].iloc[0])
    assert person1["prior_income"].iloc[1] == 60000
    assert person1["prior_income"].iloc[2] == 58000


def test_add_prior_year_features_respects_person_boundaries(sample_panel):
    """A person's first observed year must not pick up the previous
    person's last-observed value as its 'prior' value (i.e. the lag is
    computed within each person via groupby, not naively on the whole,
    sorted dataframe)."""
    out = add_prior_year_features(sample_panel, columns=["employment"])
    person2_first_row = out[(out["person_id"] == 2) & (out["year"] == 2018)]
    assert pd.isna(person2_first_row["prior_employment"].iloc[0])


def test_add_prior_year_features_custom_columns(sample_panel):
    out = add_prior_year_features(sample_panel, columns=["age"])
    assert "prior_age" in out.columns
    assert "prior_employment" not in out.columns

    person1 = out[out["person_id"] == 1].sort_values("year")
    assert person1["prior_age"].iloc[1] == 30  # person 1 was 30 in 2018


def test_add_prior_year_features_skips_missing_columns(sample_panel):
    """Columns not present in df should be skipped, not raise."""
    out = add_prior_year_features(sample_panel, columns=["age", "not_a_real_column"])
    assert "prior_age" in out.columns
    assert "prior_not_a_real_column" not in out.columns


def test_add_employment_transition_flags_entries_and_exits(sample_panel):
    """Existing coverage was only indirect via other tests - a direct test
    for this function's own logic."""
    out = add_employment_transition(sample_panel)

    person1 = out[out["person_id"] == 1].sort_values("year")
    # employment: [1, 1, 0] -> no entry, one exit (2019 -> 2020)
    assert person1["entered_employment"].sum() == 0
    assert person1["exited_employment"].sum() == 1
    assert person1[person1["year"] == 2020]["exited_employment"].iloc[0] == 1

    person2 = out[out["person_id"] == 2].sort_values("year")
    # employment: [1, 1, 1] -> no entries or exits at all
    assert person2["entered_employment"].sum() == 0
    assert person2["exited_employment"].sum() == 0
