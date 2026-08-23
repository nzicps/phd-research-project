from src.cleaning import (
    standardise_columns,
    drop_duplicate_person_years,
    flag_missing,
    restrict_age_range,
)


def test_standardise_columns():
    import pandas as pd
    df = pd.DataFrame(columns=[" Person_ID ", "YEAR"])
    out = standardise_columns(df)
    assert list(out.columns) == ["person_id", "year"]


def test_drop_duplicate_person_years(sample_panel):
    dup = sample_panel.copy()
    dup = dup._append(dup.iloc[0])  # duplicate first row
    out = drop_duplicate_person_years(dup)
    assert len(out) == len(sample_panel)


def test_flag_missing(sample_panel):
    out = flag_missing(sample_panel, ["business_id"])
    assert "business_id_missing" in out.columns
    assert out["business_id_missing"].sum() == 4


def test_restrict_age_range(sample_panel):
    out = restrict_age_range(sample_panel, min_age=40, max_age=50)
    assert (out["age"] >= 40).all()
    assert (out["age"] <= 50).all()


def test_restrict_age_range_returns_unchanged_when_no_age_column(sample_panel):
    """If age_col isn't in the dataframe, the function should return df
    as-is rather than raising a KeyError."""
    df_no_age = sample_panel.drop(columns=["age"])
    out = restrict_age_range(df_no_age, min_age=40, max_age=50)
    assert len(out) == len(df_no_age)
    assert "age" not in out.columns
