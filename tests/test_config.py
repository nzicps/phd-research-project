from src.config import load_config, CONFIG_PATH


def test_load_config_default_path_returns_expected_structure():
    """Loads the real config/research_config.yaml - this doubles as a
    check that the actual project config file is valid YAML with the
    keys the rest of the codebase (and notebooks) rely on."""
    config = load_config()
    assert config["project"]["researcher"] == "Osman Hassan Osman"
    assert "cohort" in config
    assert "propensity_score" in config
    assert config["propensity_score"]["caliper_scale"] == "logit_sd"


def test_load_config_custom_path(tmp_path):
    custom_config = tmp_path / "custom_config.yaml"
    custom_config.write_text("project:\n  name: test project\n")

    config = load_config(custom_config)
    assert config["project"]["name"] == "test project"


def test_default_config_path_points_at_real_file():
    assert CONFIG_PATH.exists()
    assert CONFIG_PATH.name == "research_config.yaml"
