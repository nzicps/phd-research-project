# Results register & living document workflow

## The problem

Across a multi-year PhD you will generate far more outputs (figures,
tables, model runs) than end up in the thesis. Once working with real
IDI/LBD data, outputs only leave the Stats NZ secure environment in
irregular batches after output checking — not continuously. Without a
system, it's easy to lose track of which output answers which research
question, which code version produced it, and whether it's actually
cleared for use outside the secure environment yet.

## The system

**`docs/results_register.csv`** — one row per output, tracked in git
(metadata only, never data). Every figure/table/result worth keeping gets
logged here via `src/results_register.log_output()`, with a status:

- `draft` — produced on synthetic data, or a real-data result still
  inside the secure environment and not yet submitted for checking.
- `pending_check` — submitted to Stats NZ output checking, awaiting
  clearance.
- `cleared` — approved for release; safe to use outside the secure
  environment (papers, thesis chapters, supervisor emails).
- `superseded` — replaced by a newer version; kept for the audit trail
  rather than deleted.

**`outputs/cleared/`** — the *only* outputs folder that is git-tracked
(unlike `outputs/figures/` and `outputs/tables/`, which stay gitignored).
Once something clears output checking, copy the actual file here and
point the register's `file_path` at it. This folder becomes your
permanent, versioned record of everything you're actually allowed to
show people.

**`scripts/compile_results.py`** — regenerates a single compiled document
(`docs/results_compendium.md` by default) from every `cleared` entry in
the register, grouped by research question. This is the "living
document": you don't hand-maintain it, you regenerate it whenever you
need an up-to-date view — a supervisor meeting, a milestone, or final
thesis submission.

## Day-to-day usage

From inside a notebook, right after saving a figure or table:

```python
from src.results_register import log_output

fig, ax = plot_yearly_trend(summary, ..., save_path="../outputs/figures/income_trend.png")

log_output(
    output_id="fig_income_trend_by_year",
    source="notebooks/07_longitudinal.ipynb",
    research_question="RQ2 — entrepreneurial engagement and income",
    description="Mean income by year, by chronic condition status",
    file_path="outputs/figures/income_trend.png",
    status="draft",
    decision_log_ref="2026-08-23 — cohort window decision",
)
```

When a batch of outputs comes back from Stats NZ output checking:

```python
from src.results_register import mark_status
mark_status("fig_income_trend_by_year", "cleared")
```

...then move the actual (checked, approved) file into `outputs/cleared/`,
update `file_path` in the register to match, and commit.

To regenerate the living document at any point:

```bash
python scripts/compile_results.py
# or, to also see your own drafts while still on synthetic data:
python scripts/compile_results.py --status draft pending_check cleared --output docs/results_compendium_DRAFT.md
```

## Why this shape

- **Traceability.** Every output links back to the notebook that made it,
  the research question it addresses, and (optionally) the decisions-log
  entry explaining a methodological choice behind it. Three years from
  now, "why does this number look like this" has an answer.
- **Respects the output-checking boundary.** The register can hold
  `draft`/`pending_check` entries that reference files still sitting
  inside the secure environment or in your local gitignored
  `outputs/figures/`; nothing confidential is ever implied by the
  register itself, since it's just metadata and status labels.
- **Compiles, rather than being hand-maintained.** A hand-maintained
  "master results doc" drifts out of sync and duplicates information
  that's really in your notebooks. Regenerating it from the register
  keeps one source of truth.
- **Git gives you the audit trail for free.** Because the register and
  `outputs/cleared/` are both version-controlled, you can see exactly
  when each result was added, changed, or superseded — useful for your
  methods chapter and for responding to examiner questions about how a
  particular figure came about.
