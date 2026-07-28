"""Tests for loading and validating config.json."""

import json
from pathlib import Path

import pytest

from jyy_amfam_toolkit.core.config import ConfigError, DevServer, load_config


def test_returns_none_when_file_does_not_exist(tmp_path: Path) -> None:
    assert load_config(tmp_path / "does-not-exist.json") is None


def test_loads_full_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "ad_username": "jyoung",
                "dev_servers": [
                    {
                        "name": "dev-web-1",
                        "address": "10.0.0.5",
                        "purpose": "web frontend testing",
                        "environment": "dev",
                    }
                ],
            }
        )
    )

    config = load_config(config_path)

    assert config is not None
    assert config.ad_username == "jyoung"
    assert config.dev_servers == [
        DevServer(
            name="dev-web-1",
            address="10.0.0.5",
            purpose="web frontend testing",
            environment="dev",
        )
    ]


def test_loads_empty_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{}")

    config = load_config(config_path)

    assert config is not None
    assert config.ad_username is None
    assert config.dev_servers == []


def test_dev_server_optional_fields_default_to_none(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"dev_servers": [{"name": "minimal", "address": "10.0.0.1"}]})
    )

    config = load_config(config_path)

    assert config is not None
    assert config.dev_servers[0].purpose is None
    assert config.dev_servers[0].environment is None


def test_raises_config_error_on_invalid_json(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text("{not valid json")

    with pytest.raises(ConfigError):
        load_config(config_path)


def test_raises_config_error_on_missing_required_field(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"dev_servers": [{"name": "no-address"}]}))

    with pytest.raises(ConfigError):
        load_config(config_path)


def test_raises_config_error_on_wrong_type(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"dev_servers": "not-a-list"}))

    with pytest.raises(ConfigError):
        load_config(config_path)


def test_example_config_file_is_valid() -> None:
    """Regression test: config.example.json must stay valid and in sync
    with the DevServer/ToolkitConfig schema."""
    example_path = Path(__file__).parent.parent / "config.example.json"

    config = load_config(example_path)

    assert config is not None
    assert config.ad_username is not None
    assert len(config.dev_servers) > 0
