import yaml
from fortune_teller.core.config_manager import ConfigManager


def test_first_run_persists_defaults(tmp_path):
    path = tmp_path / "nested" / "config.yaml"
    manager = ConfigManager(str(path))
    assert yaml.safe_load(path.read_text()) == manager.get_config()
    manager.set_value("llm.provider", "mock")
    assert manager.save_config()
    assert ConfigManager(str(path)).get_value("llm.provider") == "mock"
