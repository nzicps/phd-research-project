import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure the repo root is importable as `src...`
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def sample_panel() -> pd.DataFrame:
    """A tiny hand-built person-year panel for unit tests."""
    return pd.DataFrame({
        "person_id": [1, 1, 1, 2, 2, 2],
        "year": [2018, 2019, 2020, 2018, 2019, 2020],
        "age": [30, 31, 32, 45, 46, 47],
        "sex": ["F", "F", "F", "M", "M", "M"],
        "education": ["bachelor"] * 6,
        "chronic_condition": [0, 1, 1, 0, 0, 1],
        "employment": [1, 1, 0, 1, 1, 1],
        "self_employed": [0, 0, 0, 0, 1, 1],
        "business_id": [None, None, None, None, "B0001", "B0001"],
        "income": [60000, 58000, 0, 70000, 72000, 71000],
    })
