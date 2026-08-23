# Analysis Plan

## Notebook sequence

| Notebook | Purpose |
|---|---|
| `01_environment.ipynb` | Confirm environment works; load synthetic data |
| `02_data_structure.ipynb` | Explore synthetic dataset structure and quality |
| `03_cohort.ipynb` | Build the analytical cohort |
| `04_health.ipynb` | Construct health/chronic-condition variables |
| `05_employment.ipynb` | Construct employment variables |
| `06_entrepreneurship.ipynb` | Construct entrepreneurship/business variables |
| `07_longitudinal.ipynb` | Describe trajectories over time |
| `08_propensity_score.ipynb` | Estimate propensity scores, check balance |
| `09_robustness.ipynb` | Robustness / sensitivity analysis |
| `10_integrated_framework.ipynb` | Bring the pieces together into one framework |

## Principle

Each notebook should mostly consist of:
1. A short markdown statement of the question being addressed in this step.
2. Calls into `src/` functions (tested via `tests/`).
3. A figure/table saved into `outputs/`.
4. A short markdown interpretation.

Notebooks should NOT contain large blocks of untested logic — that belongs
in `src/`, where it can be unit tested.
