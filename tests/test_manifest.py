"""Tests for the aerosmart integration manifest."""

import json
from pathlib import Path
from typing import Any


def test_uses_home_assistant_shared_modbus_dependency() -> None:
    """Use Home Assistant's Modbus lifecycle instead of private requirements."""
    manifest_path = (
        Path(__file__).parents[1] / "custom_components" / "aerosmart" / "manifest.json"
    )
    manifest: dict[str, Any] = json.loads(manifest_path.read_text())

    assert manifest["dependencies"] == ["modbus"]
    assert "requirements" not in manifest
