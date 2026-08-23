import pandas as pd
import pytest

from src.data_loader import load_data, load_local_data


def test_load_local_csv(tmp_path, sample_panel):
    csv_path = tmp_path / "export.csv"
    sample_panel.to_csv(csv_path, index=False)

    out = load_local_data(csv_path)
    assert len(out) == len(sample_panel)
    assert list(out.columns) == list(sample_panel.columns)


def test_load_data_local_source(tmp_path, sample_panel):
    csv_path = tmp_path / "export.csv"
    sample_panel.to_csv(csv_path, index=False)

    out = load_data("local", path=csv_path)
    assert len(out) == len(sample_panel)


def test_load_data_local_requires_path():
    with pytest.raises(ValueError):
        load_data("local")


def test_load_local_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_local_data("/no/such/file.csv")


def test_load_local_unsupported_extension(tmp_path):
    bad_path = tmp_path / "data.json"
    bad_path.write_text("{}")
    with pytest.raises(ValueError):
        load_local_data(bad_path)


def test_load_local_excel(tmp_path, sample_panel):
    xlsx_path = tmp_path / "export.xlsx"
    sample_panel.to_excel(xlsx_path, index=False)

    out = load_local_data(xlsx_path)
    assert len(out) == len(sample_panel)


def test_load_data_idi_raises_outside_environment():
    with pytest.raises(NotImplementedError):
        load_data("idi")


def test_load_local_tsv(tmp_path, sample_panel):
    tsv_path = tmp_path / "export.tsv"
    sample_panel.to_csv(tsv_path, sep="\t", index=False)

    out = load_local_data(tsv_path)
    assert len(out) == len(sample_panel)
    assert list(out.columns) == list(sample_panel.columns)


def test_load_local_parquet(tmp_path, sample_panel):
    parquet_path = tmp_path / "export.parquet"
    sample_panel.to_parquet(parquet_path, index=False)

    out = load_local_data(parquet_path)
    assert len(out) == len(sample_panel)
    assert list(out.columns) == list(sample_panel.columns)


def test_load_local_stata(tmp_path, sample_panel):
    dta_path = tmp_path / "export.dta"
    # Stata column names can't start with certain characters or be too long,
    # and doesn't support None in object columns the way CSV/Parquet do -
    # sample_panel's business_id column has None values, which pandas
    # writes fine but reads back as NaN; only check the columns/shape here.
    stata_df = sample_panel.copy()
    stata_df["business_id"] = stata_df["business_id"].fillna("")
    stata_df.to_stata(dta_path, write_index=False)

    out = load_local_data(dta_path)
    assert len(out) == len(stata_df)
    assert list(out.columns) == list(stata_df.columns)


def test_load_data_synthetic_source(tmp_path, sample_panel):
    synthetic_path = tmp_path / "synthetic_idi_lbd.csv"
    sample_panel.to_csv(synthetic_path, index=False)

    out = load_data("synthetic", path=synthetic_path)
    assert len(out) == len(sample_panel)
    assert list(out.columns) == list(sample_panel.columns)


def test_load_data_synthetic_missing_file_raises(tmp_path):
    missing_path = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError, match="generate_data.py"):
        load_data("synthetic", path=missing_path)


def test_load_data_unknown_source_raises():
    with pytest.raises(ValueError, match="Unknown data source"):
        load_data("not_a_real_source")


def test_load_local_sav_without_pyreadstat_raises_helpful_error(tmp_path, monkeypatch):
    """pyreadstat isn't a project dependency (only needed for .sav files),
    so in this test environment the ImportError path is the one that's
    actually exercised - which is itself worth covering, since it's the
    error message most users hitting a .sav file will actually see."""
    sav_path = tmp_path / "export.sav"
    sav_path.write_bytes(b"not a real sav file, just needs to exist")

    import sys
    monkeypatch.setitem(sys.modules, "pyreadstat", None)
    with pytest.raises(ImportError, match="pyreadstat"):
        load_local_data(sav_path)


def test_load_local_sav_reads_successfully_when_pyreadstat_available(tmp_path, sample_panel):
    """pyreadstat is an optional dependency (only needed for .sav files,
    not listed in requirements.txt) - skip if it isn't installed rather
    than failing, since a missing optional dependency isn't a bug."""
    pyreadstat = pytest.importorskip("pyreadstat")

    sav_path = tmp_path / "export.sav"
    pyreadstat.write_sav(sample_panel.fillna(""), str(sav_path))

    out = load_local_data(sav_path)
    assert len(out) == len(sample_panel)


def test_load_local_kwargs_passed_through(tmp_path, sample_panel):
    """Extra kwargs (e.g. dtype=) should reach the underlying pandas reader."""
    csv_path = tmp_path / "export.csv"
    sample_panel.to_csv(csv_path, index=False)

    out = load_local_data(csv_path, dtype={"person_id": str})
    assert out["person_id"].dtype == object
    assert out["person_id"].iloc[0] == "1"
