"""Plotting helpers built on matplotlib/seaborn.

Keeping plotting functions here (rather than inline in notebooks) makes
figures reproducible and testable, and keeps a consistent style across the
thesis.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


def plot_yearly_trend(summary_df, year_col: str, value_col: str,
                       title: str = "", ylabel: str = "",
                       save_path: Path = None):
    """Line plot of a summarised value over time; optionally saves to file."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.lineplot(data=summary_df, x=year_col, y=value_col, marker="o", ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel(ylabel or value_col)
    fig.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    return fig, ax


def plot_covariate_balance(balance_df, save_path: Path = None):
    """Bar plot of standardised mean differences from check_covariate_balance()."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=balance_df, x="smd", y="covariate", ax=ax)
    ax.axvline(0.1, color="red", linestyle="--", linewidth=1)
    ax.axvline(-0.1, color="red", linestyle="--", linewidth=1)
    ax.set_title("Covariate balance (standardised mean differences)")
    ax.set_xlabel("Standardised mean difference")
    fig.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150)

    return fig, ax
