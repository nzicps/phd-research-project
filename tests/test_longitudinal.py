import pandas as pd

from src.longitudinal import yearly_summary, transition_matrix


def test_yearly_summary_computes_mean_by_year(sample_panel):
    summary = yearly_summary(sample_panel, value_col="income", year_col="year")
    assert list(summary.columns) == ["year", "mean_income"]
    assert set(summary["year"]) == {2018, 2019, 2020}
    row_2018 = summary.loc[summary["year"] == 2018, "mean_income"].iloc[0]
    assert row_2018 == (60000 + 70000) / 2


def test_yearly_summary_supports_other_aggregations(sample_panel):
    summary = yearly_summary(sample_panel, value_col="income", year_col="year", agg="max")
    assert "max_income" in summary.columns
    row_2018 = summary.loc[summary["year"] == 2018, "max_income"].iloc[0]
    assert row_2018 == 70000


def test_transition_matrix_counts_consecutive_year_transitions(sample_panel):
    matrix = transition_matrix(sample_panel, state_col="employment")
    assert {"from_state", "to_state", "count"}.issubset(matrix.columns)
    # person 1: employment 1 -> 1 -> 0 across 2018-19-20 gives one 1->1 and one 1->0
    # person 2: employment 1 -> 1 -> 1 gives two 1->1 transitions
    total_transitions = matrix["count"].sum()
    assert total_transitions == 4  # 2 consecutive pairs per person x 2 people

    row_1_to_0 = matrix[(matrix["from_state"] == 1) & (matrix["to_state"] == 0)]
    assert row_1_to_0["count"].iloc[0] == 1


def test_transition_matrix_skips_non_consecutive_years():
    df = pd.DataFrame({
        "person_id": [1, 1, 1],
        "year": [2018, 2019, 2021],  # gap between 2019 and 2021
        "employment": [1, 0, 1],
    })
    matrix = transition_matrix(df, state_col="employment")
    # Only the 2018->2019 pair is consecutive; 2019->2021 is skipped.
    assert matrix["count"].sum() == 1
