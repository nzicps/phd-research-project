"""Generate a synthetic IDI/LBD-style panel dataset for development and testing.

This produces entirely fabricated data with a similar shape to what a real
person-year (linked to business) IDI/LBD extract might look like — NOT real
data, and not modelled on any real individual. Safe to commit to GitHub.

Usage
-----
python synthetic/generate_data.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "data" / "synthetic" / "synthetic_idi_lbd.csv"

N_PEOPLE = 2000
START_YEAR = 2015
END_YEAR = 2023
SEED = 42


def generate_synthetic_panel(n_people: int = N_PEOPLE,
                              start_year: int = START_YEAR,
                              end_year: int = END_YEAR,
                              seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    years = list(range(start_year, end_year + 1))

    records = []
    business_counter = 1

    sexes = rng.choice(["M", "F"], size=n_people)
    base_ages = rng.integers(20, 60, size=n_people)
    educations = rng.choice(
        ["secondary", "certificate", "bachelor", "postgraduate"],
        size=n_people, p=[0.35, 0.25, 0.28, 0.12]
    )

    for i in range(n_people):
        person_id = 1000 + i
        chronic = 0
        employed = 1
        self_employed = 0
        business_id = None
        income = max(rng.normal(55000, 15000), 0)

        # a person has some baseline annual probability of chronic condition
        # onset that, once it occurs, persists (with small remission chance)
        onset_prob = rng.uniform(0.01, 0.05)
        remission_prob = 0.05
        exit_employment_prob = 0.04
        enter_self_employment_prob = 0.03
        exit_self_employment_prob = 0.15

        for year in years:
            age = base_ages[i] + (year - start_year)

            # health transitions
            if chronic == 0 and rng.random() < onset_prob:
                chronic = 1
            elif chronic == 1 and rng.random() < remission_prob:
                chronic = 0

            # employment transitions (chronic condition slightly raises
            # exit probability, for a plausible synthetic signal)
            exit_prob = exit_employment_prob + (0.03 if chronic else 0)
            if employed == 1 and rng.random() < exit_prob:
                employed = 0
            elif employed == 0 and rng.random() < 0.25:
                employed = 1

            # self-employment transitions
            if employed == 1 and self_employed == 0 and rng.random() < enter_self_employment_prob:
                self_employed = 1
                business_id = f"B{business_counter:04d}"
                business_counter += 1
            elif self_employed == 1 and rng.random() < exit_self_employment_prob:
                self_employed = 0
                employed = rng.choice([0, 1], p=[0.3, 0.7])
                business_id = None

            # income evolves with noise; drops if not employed
            if employed == 0:
                income = 0
            else:
                drift = rng.normal(1500, 3000)
                penalty = -4000 if chronic else 0
                income = max(income + drift + penalty, 0)

            records.append({
                "person_id": person_id,
                "year": year,
                "age": age,
                "sex": sexes[i],
                "education": educations[i],
                "chronic_condition": chronic,
                "employment": employed,
                "self_employed": self_employed,
                "business_id": business_id,
                "income": round(income, 2),
            })

    df = pd.DataFrame.from_records(records)
    return df


def main():
    df = generate_synthetic_panel()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {len(df):,} rows for {df['person_id'].nunique():,} people "
          f"to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
