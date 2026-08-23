# Data Requirements

## Data sources (candidate)

| Source | Purpose | Access |
|---|---|---|
| IDI (Integrated Data Infrastructure) | Person-level health, employment, income data | Requires approved Stats NZ / UoA application |
| LBD (Longitudinal Business Database) | Business entry, survival, employee counts | Requires approved Stats NZ / UoA application |
| DataInfo+ | Metadata on IDI/LBD variables and collections, to identify candidate variables before applying for access | Public metadata tool |
| Synthetic data (this repo) | Development and testing without confidential data | `synthetic/generate_data.py` |

## Security principle

```
CODE               → GitHub
DOCUMENTATION      → GitHub
SYNTHETIC DATA     → GitHub (safe, fabricated)
PUBLIC DATA        → GitHub, if genuinely public and license permits
IDI MICRODATA      → NEVER on GitHub / this computer
LBD MICRODATA      → NEVER on GitHub / this computer
CREDENTIALS        → NEVER on GitHub
```

Confidential data stays inside the Stats NZ-approved secure environment at
all times. This repository's `data_loader.py` is written so that switching
from `source="synthetic"` to `source="idi"` requires no change to downstream
analysis code — only the loader implementation changes, and only within the
approved environment.

## Candidate variable groups (to refine using DataInfo+)

- **Health**: chronic condition flags/diagnoses, health system utilisation
- **Employment**: employment status, income (wages/salaries)
- **Business (LBD)**: business entry, employee counts, survival/exit
- **Demographic**: age, sex, education, region
- **Outcome**: income, income stability/variance, wellbeing proxies

See `variable_dictionary.csv` for the working dictionary — to be populated
with actual IDI/LBD table and variable names once access is confirmed.
