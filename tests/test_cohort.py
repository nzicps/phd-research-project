from src.cohort import build_cohort, require_balanced_panel, cohort_summary


def test_build_cohort_window(sample_panel):
    out = build_cohort(sample_panel, start_year=2019, end_year=2020)
    assert out["year"].min() == 2019
    assert out["year"].max() == 2020


def test_require_balanced_panel(sample_panel):
    out = require_balanced_panel(sample_panel, start_year=2018, end_year=2020)
    # both people in sample_panel are observed all 3 years
    assert out["person_id"].nunique() == 2


def test_cohort_summary(sample_panel):
    summary = cohort_summary(sample_panel)
    assert summary["n_unique_people"] == 2
    assert summary["n_person_years"] == 6
    assert summary["min_year"] == 2018
    assert summary["max_year"] == 2020
