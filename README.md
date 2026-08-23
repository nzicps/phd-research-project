# Developing an Integrated Framework for Evaluating Health and Entrepreneurship Outcomes for Individuals with Chronic Health Conditions in Aotearoa New Zealand

PhD research computing framework — Osman Hassan Osman, Faculty of Arts and
Education, Social Sciences, University of Auckland. Proposed supervisor:
Professor Barry Milne.

## Research focus

Health is a fundamental determinant of individual wellbeing, but individuals
living with chronic health conditions often face constraints on economic
participation. Entrepreneurship offers an alternative, flexible pathway to
economic participation — but can itself introduce demands and pressures that
affect health. Health and entrepreneurship investments in Aotearoa New
Zealand are currently designed and evaluated independently. This research
develops an **integrated framework** for evaluating how health and
entrepreneurship interact to shape economic participation, income,
stability, and wellbeing outcomes for people with chronic health conditions.

The project is mixed-methods:
- **Quantitative**: linked IDI (Integrated Data Infrastructure) and LBD
  (Longitudinal Business Database) administrative data, analysed via
  propensity-score matching and longitudinal methods.
- **Qualitative**: document analysis of NZ health and entrepreneurship
  policy/programme materials, informing the conceptual model.

See `docs/research_questions.md`, `docs/methodology.md`, and
`docs/scholarly_context.md` for the full detail (drawn from the Faculty of
Arts and Education Initial Statement of Research Intent).

See `docs/data_import_guide.md` for how to load your own local files
(CSV/Excel/Parquet/Stata/SPSS) or, eventually, IDI data.

## Data

The research is designed to use approved New Zealand administrative data,
including the IDI and LBD, administered by Stats NZ under the Five Safes
framework. **No confidential IDI/LBD microdata is stored in this
repository** — only synthetic and public data live here.

## Research environment

Python · JupyterLab · Pandas · NumPy · Statsmodels · Scikit-learn ·
linearmodels · lifelines

SciPy, DuckDB, and PyArrow are installed and available (see
`environment.yml`/`requirements.txt`) but not yet exercised by any
analysis code — they're there for when a query, out-of-memory dataset,
or Parquet workflow needs them, most likely once working with the full
IDI/LBD extract.

## Repository structure

```
phd-idi-lbd-framework/
├── README.md
├── LICENSE
├── .gitignore
├── environment.yml
├── requirements.txt
├── config/                 research configuration (paths, params)
├── docs/                   research documentation, decision log & results register
├── src/                    reusable, tested research code
├── notebooks/              analysis notebooks (call into src/)
├── scripts/                standalone scripts, e.g. compile_results.py
├── synthetic/              synthetic IDI/LBD-style data generator
├── tests/                  automated tests (pytest)
├── outputs/                figures and tables (drafts gitignored; outputs/cleared/ is tracked)
└── .github/workflows/      CI: run tests automatically on push
```

## Quick start

```bash
git clone https://github.com/nzicps/phd-research-project.git
cd phd-research-project

# Option A: conda
conda env create -f environment.yml
conda activate phd_idi

# Option B: pip
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Generate synthetic data
python synthetic/generate_data.py

# Run tests
pytest

# Launch Jupyter
jupyter lab
```

Then open `notebooks/01_environment.ipynb` and run all cells.

## Design principles

1. **Portability.** `src/data_loader.py` abstracts the data source
   (`"synthetic"` vs `"idi"`) so the same analysis code runs locally and
   (eventually, subject to Stats NZ/UoA approval) inside the IDI environment.
2. **Notebooks are thin.** Notebooks call functions in `src/`; they should
   not contain hundreds of lines of untested logic.
3. **Everything is tested.** `tests/` uses `pytest` and runs automatically
   via GitHub Actions on every push.
4. **Everything is logged.** `docs/decisions_log.md` records methodological
   decisions and why they were made. `docs/results_register.csv` and
   `scripts/compile_results.py` track every output (figure/table/model
   result) back to the research question and code that produced it, and
   compile everything that has cleared output checking into a single
   living document — see `docs/results_workflow.md`.
5. **The security boundary is respected, not engineered around.** Code and
   documentation live on GitHub. Confidential microdata never does.

## License

See `LICENSE`. Choose a license appropriate for your institution's policy —
an MIT license is included as a placeholder.
