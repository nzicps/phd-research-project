# Methodology

Source: Statement of Research Intent, Section 4 (Research design).

## Overview

This is a **mixed-methods** study examining the relationship between health
and entrepreneurship for individuals living with chronic health conditions
in Aotearoa New Zealand.

1. **Health as the primary dimension.** How chronic health conditions
   influence individuals' capacity to participate in economic activities
   (employment and entrepreneurship). Central factors: access to services,
   health status, functional capacity.
2. **Entrepreneurship as economic participation.** How individuals with
   different health profiles engage in entrepreneurial activity, and how
   that engagement relates to income, stability, and wellbeing.
3. **Quantitative component** — linked IDI + LBD administrative data,
   analysed longitudinally.
4. **Qualitative component** — document analysis of relevant NZ policy and
   programme materials, examining how health and entrepreneurship are
   currently conceptualised, measured, and supported. Feeds into the
   conceptual model.
5. **Integration** — the final output is a single integrated evaluation
   framework spanning health, economic participation, and wellbeing.

This repository currently scaffolds stage 3 (the quantitative pipeline).
The qualitative document-analysis component (stage 4) is not yet
represented in code — it would likely live as a separate `docs/` /
`qualitative/` workstream feeding into the same conceptual framework in
`docs/conceptual_framework.md` (see the earlier discussion's IDI/LBD
research map for a starting shape).

## Planned quantitative analytical stages (this repo's `src/`)

1. **Cohort construction** (`src/cohort.py`) — define the analytical
   population and observation window.
2. **Variable construction** (`src/health.py`, `src/employment.py`,
   `src/entrepreneurship.py`) — derive exposures, outcomes and covariates.
3. **Longitudinal / descriptive analysis** (`src/longitudinal.py`).
4. **Propensity-score analysis** (`src/causal.py`) — estimate propensity
   scores, assess covariate balance (Rosenbaum & Rubin, 1983), match or
   weight.
5. **Regression / outcome models** (`src/models.py`, `src/panel_models.py`)
   — cross-sectional regression and panel fixed-effects models estimating
   relationships between health, entrepreneurial activity, and economic
   outcomes.
6. **Survival analysis** (`src/survival.py`) — Kaplan-Meier and Cox
   proportional-hazards models of business survival, built on
   `src/entrepreneurship.compute_business_survival_with_covariates()`.
7. **Robustness checks** — alternative specifications, placebo tests,
   sensitivity analysis.

## Estimation approach (per the Statement of Research Intent)

- Primary design: **propensity-score matching** to compare individuals
  with similar characteristics, strengthening robustness of findings
  within observational (non-experimental) IDI/LBD data.
- **Longitudinal analysis** exploiting the panel structure of IDI/LBD to
  track health status, labour-market participation, and business activity
  over time — implemented as panel fixed-effects regression in
  `src/panel_models.py` (`linearmodels.PanelOLS`), controlling for
  time-invariant person-level heterogeneity (and, optionally, year
  effects).
- Secondary/robustness: regression adjustment, and (where business
  survival is the outcome) survival models via `lifelines`
  (`src/survival.py`) — Kaplan-Meier curves and a Cox proportional-hazards
  model. See that module's docstring for the event-vs-censoring
  assumption used, which should be confirmed against the real IDI/LBD
  business-exit definition before relying on it.

## Reproducibility

- All analysis logic lives in `src/`, imported by notebooks — not
  duplicated across notebooks.
- Random seeds are fixed via `config/research_config.yaml`.
- Every methodological choice is recorded in `decisions_log.md`.
