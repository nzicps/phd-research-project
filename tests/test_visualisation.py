import matplotlib
matplotlib.use("Agg")  # headless backend for CI/testing - no display needed

import pandas as pd

from src.visualisation import plot_yearly_trend, plot_covariate_balance


def test_plot_yearly_trend_returns_fig_and_ax():
    summary = pd.DataFrame({"year": [2018, 2019, 2020], "mean_income": [50000, 51000, 49000]})
    fig, ax = plot_yearly_trend(summary, year_col="year", value_col="mean_income")

    assert fig is not None
    assert ax is not None
    assert ax.get_xlabel() == "Year"


def test_plot_yearly_trend_saves_file(tmp_path):
    summary = pd.DataFrame({"year": [2018, 2019], "mean_income": [50000, 51000]})
    save_path = tmp_path / "figures" / "trend.png"

    plot_yearly_trend(summary, year_col="year", value_col="mean_income", save_path=save_path)

    # save_path's parent directory should have been created automatically,
    # and the file should exist and be non-empty.
    assert save_path.exists()
    assert save_path.stat().st_size > 0


def test_plot_covariate_balance_returns_fig_and_ax():
    balance = pd.DataFrame({
        "covariate": ["age", "prior_income"],
        "treated_mean": [45.0, 50000.0],
        "control_mean": [44.0, 49000.0],
        "smd": [0.05, 0.15],
    })
    fig, ax = plot_covariate_balance(balance)

    assert fig is not None
    assert ax.get_xlabel() == "Standardised mean difference"


def test_plot_covariate_balance_saves_file(tmp_path):
    balance = pd.DataFrame({
        "covariate": ["age"],
        "treated_mean": [45.0],
        "control_mean": [44.0],
        "smd": [0.05],
    })
    save_path = tmp_path / "tables" / "balance.png"

    plot_covariate_balance(balance, save_path=save_path)

    assert save_path.exists()
    assert save_path.stat().st_size > 0
