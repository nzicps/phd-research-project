"""Load the central research configuration.

Keeping a single config loader means paths and parameters are defined once,
in config/research_config.yaml, rather than scattered/hard-coded through
notebooks and src modules.
"""

from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "config" / "research_config.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Load research_config.yaml and return it as a dict.

    Parameters
    ----------
    path : Path
        Path to the YAML config file. Defaults to config/research_config.yaml
        at the repository root.
    """
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config
