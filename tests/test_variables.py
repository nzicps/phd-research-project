from src.health import add_chronic_condition_onset, add_condition_duration
from src.employment import add_employment_transition
from src.entrepreneurship import add_business_entry, compute_business_survival


def test_add_chronic_condition_onset(sample_panel):
    out = add_chronic_condition_onset(sample_panel)
    # person 1 first has the condition in 2019
    p1 = out[out["person_id"] == 1]
    onset_row = p1[p1["chronic_onset_flag"] == 1]
    assert onset_row["year"].iloc[0] == 2019


def test_add_condition_duration(sample_panel):
    out = add_condition_duration(sample_panel)
    p1 = out[out["person_id"] == 1].sort_values("year")
    # condition present in 2019 and 2020 -> durations 1, 2
    assert list(p1["chronic_condition_duration"]) == [0, 1, 2]


def test_add_employment_transition(sample_panel):
    out = add_employment_transition(sample_panel)
    p1 = out[out["person_id"] == 1].sort_values("year")
    # person 1: employed, employed, not employed -> exit in 2020
    assert p1[p1["year"] == 2020]["exited_employment"].iloc[0] == 1


def test_add_business_entry(sample_panel):
    out = add_business_entry(sample_panel)
    p2 = out[out["person_id"] == 2].sort_values("year")
    entry_row = p2[p2["business_entry_flag"] == 1]
    assert entry_row["year"].iloc[0] == 2019


def test_compute_business_survival(sample_panel):
    survival = compute_business_survival(sample_panel)
    row = survival[survival["business_id"] == "B0001"].iloc[0]
    assert row["entry_year"] == 2019
    assert row["last_observed_year"] == 2020
    assert row["survival_years"] == 2
