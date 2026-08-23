# Synthetic Data

`generate_data.py` produces a fabricated person-year panel dataset with a
similar shape to a hypothetical IDI/LBD extract:

- `person_id`, `year`
- `age`, `sex`, `education`
- `chronic_condition` (0/1)
- `employment` (0/1)
- `self_employed` (0/1)
- `business_id` (links self-employed person-years to a fabricated business)
- `income`

This is **not** real data, is **not** modelled on any real individual, and
contains no information derived from IDI/LBD. It exists purely to let the
analytical pipeline (`src/`, `notebooks/`) be built and tested before IDI
access is granted.

Run:

```bash
python synthetic/generate_data.py
```

This writes `data/synthetic/synthetic_idi_lbd.csv` (git-ignored by default
under the `data/` rule in `.gitignore`, though synthetic data is generally
safe to commit if you choose to — see `docs/data_requirements.md`).
