"""Tests for config loading, including the newer processing/cleanup/admin
sections added ahead of Pi transfer."""
from pathlib import Path

from app.core.config import Config


def _write_yaml(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(content)
    return config_path


def test_defaults_when_no_file_present(tmp_path):
    config = Config.load(tmp_path / "does_not_exist.yaml")

    assert config.processing.template == "classic"
    assert config.processing.filter is None
    assert config.cleanup.enabled is True
    assert config.cleanup.max_age_days == 30
    assert config.cleanup.run_on_startup is True
    assert config.admin.enabled is True
    assert config.admin.hold_seconds == 5.0


def test_processing_section_overrides(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        processing:
          template: wedding
          filter: sepia
        """,
    )

    config = Config.load(path)

    assert config.processing.template == "wedding"
    assert config.processing.filter == "sepia"


def test_cleanup_section_overrides(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        cleanup:
          enabled: false
          max_age_days: 7
          run_on_startup: false
        """,
    )

    config = Config.load(path)

    assert config.cleanup.enabled is False
    assert config.cleanup.max_age_days == 7
    assert config.cleanup.run_on_startup is False


def test_admin_section_overrides(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        admin:
          enabled: false
          hold_seconds: 3
        """,
    )

    config = Config.load(path)

    assert config.admin.enabled is False
    assert config.admin.hold_seconds == 3


def test_partial_config_falls_back_to_defaults_for_missing_sections(tmp_path):
    path = _write_yaml(
        tmp_path,
        """
        booth:
          name: Test Booth
        """,
    )

    config = Config.load(path)

    assert config.booth.name == "Test Booth"
    # Sections absent from the file should still get sensible defaults.
    assert config.processing.template == "classic"
    assert config.cleanup.max_age_days == 30
    assert config.admin.hold_seconds == 5.0
