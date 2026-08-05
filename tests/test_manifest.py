"""Tests for the aerosmart integration manifest."""

import json
from pathlib import Path
from typing import Any


def test_transport_requirements_are_explicit() -> None:
    """Declare the backend separately so Home Assistant installs it."""
    manifest_path = (
        Path(__file__).parents[1] / "custom_components" / "aerosmart" / "manifest.json"
    )
    manifest: dict[str, Any] = json.loads(manifest_path.read_text())

    assert "modbus-connection==3.9.0" in manifest["requirements"]
    assert "tmodbus==0.5.0" in manifest["requirements"]
    assert all(
        "[tmodbus]" not in requirement for requirement in manifest["requirements"]
    )
