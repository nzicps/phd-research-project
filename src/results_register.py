"""A living register of every research output produced by this project.

The problem this solves
------------------------
Over a multi-year PhD, you will generate far more figures, tables, and
model results than end up in the thesis, and (once working with real
IDI/LBD data) outputs only leave the secure environment in irregular
batches after Stats NZ output-checking. Without a register, it becomes
very hard to remember, months later, which output answered which research
question, which code version produced it, or whether it has actually
cleared output checking yet.

This module keeps a single CSV register (`docs/results_register.csv`,
tracked in git — it holds only metadata, never data) that notebooks
append to whenever they produce something worth keeping. At the end of
the PhD, `compile_register()` (see `scripts/compile_results.py`) turns
every *cleared* entry into a single compiled document.

Typical use from a notebook
----------------------------
    from src.results_register import log_output

    fig, ax = plot_yearly_trend(summary, ..., save_path="../outputs/figures/income_trend.png")
    log_output(
        output_id="fig_income_trend_by_year",
        source="notebooks/07_longitudinal.ipynb",
        research_question="RQ2 — entrepreneurial engagement and income",
        description="Mean income by year, by chronic condition status",
        file_path="outputs/figures/income_trend.png",
        status="draft",  # "draft" | "pending_check" | "cleared" | "superseded"
    )
"""

from pathlib import Path
from datetime import date, datetime
import csv

from src.config import REPO_ROOT

REGISTER_PATH = REPO_ROOT / "docs" / "results_register.csv"

FIELDS = [
    "output_id",
    "date_added",
    "source",
    "research_question",
    "description",
    "status",
    "decision_log_ref",
    "file_path",
]

VALID_STATUSES = {"draft", "pending_check", "cleared", "superseded"}


def _ensure_register_exists(path: Path = REGISTER_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()


def log_output(output_id: str, source: str, research_question: str,
                description: str, file_path: str, status: str = "draft",
                decision_log_ref: str = "", register_path: Path = REGISTER_PATH) -> None:
    """Append one row to the results register.

    Parameters
    ----------
    output_id : str
        A short, stable, human-chosen identifier, e.g. "fig_income_trend".
        Reused output_ids are treated as new versions — see
        `supersede_output()` to mark the old one superseded first.
    source : str
        The notebook or script that produced this output, e.g.
        "notebooks/07_longitudinal.ipynb". Helps you find the code again.
    research_question : str
        Which research question / aim this speaks to (see
        docs/research_questions.md) — keeps every output traceable back
        to why it exists.
    description : str
        One human-readable line describing the output.
    file_path : str
        Where the output file lives, relative to the repo root. For
        "draft" status this will usually be under the gitignored
        outputs/figures or outputs/tables. For "cleared" status, move
        the actual file into outputs/cleared/ first and point file_path
        there.
    status : str
        One of "draft", "pending_check", "cleared", "superseded".
    decision_log_ref : str
        Optional pointer to the relevant docs/decisions_log.md entry
        (e.g. a date heading), so the methodological reasoning behind
        this output is one click away.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}, got {status!r}")

    _ensure_register_exists(register_path)
    with open(register_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow({
            "output_id": output_id,
            "date_added": date.today().isoformat(),
            "source": source,
            "research_question": research_question,
            "description": description,
            "status": status,
            "decision_log_ref": decision_log_ref,
            "file_path": file_path,
        })


def read_register(register_path: Path = REGISTER_PATH) -> list:
    """Return the register as a list of dicts (empty list if none logged yet)."""
    if not register_path.exists():
        return []
    with open(register_path, "r", newline="") as f:
        return list(csv.DictReader(f))


def mark_status(output_id: str, new_status: str,
                 register_path: Path = REGISTER_PATH) -> int:
    """Update the status of the most recent entry with the given output_id.

    Use this when an output moves through its lifecycle, e.g. from
    "pending_check" to "cleared" once Stats NZ has approved it for
    release, or to "superseded" when a newer version replaces it.

    Returns the number of rows updated (0 or 1).
    """
    if new_status not in VALID_STATUSES:
        raise ValueError(f"new_status must be one of {sorted(VALID_STATUSES)}, got {new_status!r}")

    rows = read_register(register_path)
    if not rows:
        return 0

    # Find the most recent (last-added) row with this output_id.
    matches = [i for i, r in enumerate(rows) if r["output_id"] == output_id]
    if not matches:
        return 0
    rows[matches[-1]]["status"] = new_status

    with open(register_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 1
