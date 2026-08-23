# Research Decisions Log

Record every non-trivial methodological decision here, chronologically.
This becomes invaluable when writing up the thesis and defending choices.

Use this template for each entry:

```
## YYYY-MM-DD

**Decision:**


**Reason:**


**Alternative(s) considered:**


**Supervisor discussion:**


**Impact on analysis:**

```

---

## 2026-08-23

**Decision:**
Started repository with a synthetic-data-first development approach, and
aligned `docs/research_questions.md`, `docs/methodology.md`,
`docs/scholarly_context.md`, and `README.md` to the Faculty of Arts and
Education Initial Statement of Research Intent submitted for this PhD.

**Reason:**
IDI access had not yet been granted; needed to build and test the
analytical pipeline against non-confidential data first, using the same
research questions and design as the approved statement of intent.

**Alternative(s) considered:**
Waiting for IDI access before writing any code — rejected as inefficient.

**Supervisor discussion:**
N/A (scaffold entry — update once discussed with Professor Barry Milne).

**Impact on analysis:**
`src/data_loader.py` built with a `source` parameter so the same downstream
code will work once switched to `"idi"`. The precise treatment/outcome
specification (chronic condition vs entrepreneurship vs entrepreneurship
support as the exposure) remains open — see `docs/research_questions.md`.

---

## 2026-08-23 (later same day)

**Decision:**
Changed `src/causal.nearest_neighbour_match()` to match on the
logit-transformed propensity score by default (`caliper_scale="logit_sd"`),
with the caliper expressed in standard deviations of that logit, rather
than as a raw probability difference. `config/research_config.yaml` and
`notebooks/08_propensity_score.ipynb` updated accordingly. Also added test
coverage for `nearest_neighbour_match()` (`tests/test_causal_matching.py`)
and for `src/longitudinal.py` (`tests/test_longitudinal.py`), neither of
which had tests before.

**Reason:**
The original implementation applied `caliper=0.2` directly to the raw
propensity score (0-1 scale). A raw-probability caliper of 0.2 is a fifth
of the entire possible range and would accept poor matches. Standard
practice (Austin, 2011, and widely followed in applied propensity-score
work) is to match on the logit of the propensity score and set the
caliper as a fraction of the pooled standard deviation of that logit — a
`caliper=0.2` under that convention is a reasonable, much tighter,
default. The old and new code both happened to use `0.2` as the default
value, which is a coincidence worth flagging: the number was almost
certainly intended as "0.2 SDs of the logit" (the standard convention)
but was being applied as "0.2 of raw probability" instead.

**Alternative(s) considered:**
Leaving raw-probability matching as the default and only adding
logit-scale as an opt-in — rejected, since logit-scale is the
recommended default in the methodological literature this project's
`docs/methodology.md` already cites (Rosenbaum & Rubin, 1983, and the
broader propensity-score literature). Raw-probability matching is kept
available via `caliper_scale="probability"` for cases where it's
deliberately wanted.

**Supervisor discussion:**
N/A — confirm the final caliper value and scale with Professor Barry
Milne before applying this to real IDI/LBD data; 0.2 SDs is a common
starting point, not a fixed rule.

**Impact on analysis:**
Matched samples produced by `nearest_neighbour_match()` will generally be
smaller and better-balanced under the new default than under the old
implementation, since the effective distance threshold is tighter. Re-run
`notebooks/08_propensity_score.ipynb` (and anything downstream of it) to
see the updated matched sample and covariate balance.

---

## 2026-08-23 (later still)

**Decision:**
Implemented the two estimation approaches that `docs/methodology.md`
already named but had no code behind: panel fixed-effects regression
(`src/panel_models.py`, built on `linearmodels.PanelOLS`) for the primary
longitudinal design, and Kaplan-Meier / Cox proportional-hazards survival
analysis (`src/survival.py`, built on `lifelines`) for business survival.
Extended `src/entrepreneurship.py` with
`compute_business_survival_with_covariates()` to join founder-level
covariates (age, sex, chronic_condition at entry) onto the existing
business survival table, since a Cox model needs covariates and the
original `compute_business_survival()` only returned durations. Wired
both into the relevant notebooks (`07_longitudinal.ipynb`,
`06_entrepreneurship.ipynb`) with a worked example against the synthetic
data, and added test coverage (`tests/test_panel_models.py`,
`tests/test_survival.py`).

**Reason:**
`docs/methodology.md` and the README's "Research environment" section
named `linearmodels` and `lifelines` as this project's actual estimation
approach, but neither had any implementation — `requirements.txt` and
`environment.yml` listed them, and nothing else did. For a project being
submitted for university review, claiming tools that aren't backed by
code is a credibility gap worth closing rather than leaving open.

**Alternative(s) considered:**
Leaving the README/methodology claims as aspirational and adding a
"planned" caveat instead of implementing now — rejected in favour of
closing the gap, since both methods were straightforward to scaffold
against the synthetic data and the repo's existing structure (thin
notebooks calling into tested `src/` functions) made this a natural fit
rather than a detour.

**Supervisor discussion:**
N/A — confirm with Professor Barry Milne, once real IDI/LBD data is
available: (a) whether entity-and-time two-way fixed effects or
entity-only is the right default for the main specification, and (b) the
correct event-vs-censoring definition for business exit (see the
"note on censoring" in `src/survival.py`'s module docstring — the current
implementation treats "still active in the final study year" as censored
and everything else as an observed exit, which conflates genuine business
closure with the founder simply leaving the observable population).

**Impact on analysis:**
`docs/methodology.md` and the README's tool list are now accurate
statements of what the codebase does, not just what it depends on. No
existing analysis output changes — these are new capabilities, not
modifications to existing ones (aside from `entrepreneurship.py` gaining
a new function; `compute_business_survival()` itself is unchanged).
