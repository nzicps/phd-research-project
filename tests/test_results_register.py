from pathlib import Path

from src.results_register import log_output, read_register, mark_status


def test_log_output_creates_register_and_writes_row(tmp_path):
    register_path = tmp_path / "results_register.csv"

    log_output(
        output_id="fig_test",
        source="notebooks/00_test.ipynb",
        research_question="RQ1",
        description="A test figure",
        file_path="outputs/figures/test.png",
        status="draft",
        register_path=register_path,
    )

    rows = read_register(register_path)
    assert len(rows) == 1
    assert rows[0]["output_id"] == "fig_test"
    assert rows[0]["status"] == "draft"
    assert rows[0]["research_question"] == "RQ1"


def test_log_output_rejects_invalid_status(tmp_path):
    register_path = tmp_path / "results_register.csv"
    try:
        log_output(
            output_id="fig_test",
            source="notebooks/00_test.ipynb",
            research_question="RQ1",
            description="A test figure",
            file_path="outputs/figures/test.png",
            status="not_a_real_status",
            register_path=register_path,
        )
        assert False, "expected a ValueError"
    except ValueError:
        pass


def test_read_register_returns_empty_list_when_no_file(tmp_path):
    register_path = tmp_path / "does_not_exist.csv"
    assert read_register(register_path) == []


def test_mark_status_updates_most_recent_matching_row(tmp_path):
    register_path = tmp_path / "results_register.csv"

    log_output(
        output_id="tbl_balance",
        source="notebooks/08_propensity_score.ipynb",
        research_question="RQ1",
        description="Covariate balance table",
        file_path="outputs/tables/balance.csv",
        status="pending_check",
        register_path=register_path,
    )

    updated = mark_status("tbl_balance", "cleared", register_path=register_path)
    assert updated == 1

    rows = read_register(register_path)
    assert rows[0]["status"] == "cleared"


def test_mark_status_returns_zero_when_register_empty(tmp_path):
    register_path = tmp_path / "does_not_exist.csv"
    updated = mark_status("anything", "cleared", register_path=register_path)
    assert updated == 0


def test_mark_status_rejects_invalid_status(tmp_path):
    register_path = tmp_path / "results_register.csv"
    log_output(
        output_id="fig_test",
        source="notebooks/00_test.ipynb",
        research_question="RQ1",
        description="A test figure",
        file_path="outputs/figures/test.png",
        status="draft",
        register_path=register_path,
    )
    try:
        mark_status("fig_test", "not_a_real_status", register_path=register_path)
        assert False, "expected a ValueError"
    except ValueError:
        pass


def test_mark_status_returns_zero_when_output_id_not_found(tmp_path):
    register_path = tmp_path / "results_register.csv"
    log_output(
        output_id="fig_test",
        source="notebooks/00_test.ipynb",
        research_question="RQ1",
        description="A test figure",
        file_path="outputs/figures/test.png",
        status="draft",
        register_path=register_path,
    )
    updated = mark_status("does_not_exist", "cleared", register_path=register_path)
    assert updated == 0
