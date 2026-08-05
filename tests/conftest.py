"""Fixtures for the aerosmart tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import CONF_HOST, CONF_PORT
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.aerosmart.const import (
    CONF_UNIT_HEAT_PUMP,
    CONF_UNIT_VENTILATION,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Make custom_components/aerosmart loadable in every test in this suite.

    Without requesting this fixture, Home Assistant's component loader
    ignores ``custom_components`` entirely, so config-entry setup would
    silently fail to find the integration.
    """


UNIT_VENTILATION = 1
UNIT_HEAT_PUMP = 2

# uint32 fields span 2 registers, big word order: [high_word, low_word].
VENTILATION_HOLDING: dict[int, list[int]] = {
    1174: [0, 3],  # general.wochentag
    202: [0, 123],  # outside_temperature.temp_aussenluft (scale 0.001 -> 0.123)
}
HEAT_PUMP_HOLDING: dict[int, list[int]] = {
    1044: [0, 1],  # heat_pump.waermepumpe
    212: [0, 45000],  # hot_water_heat_pump.warmwasser_speicher_oben (-> 45.0)
}


@pytest.fixture
def mock_modbus_unit_ventilation(
    mock_modbus_connection: MockModbusConnection,
) -> MockModbusUnit:
    """A seeded aerosmart ventilation unit (Modbus unit 1)."""
    unit = mock_modbus_connection.for_unit(UNIT_VENTILATION)
    for address, words in VENTILATION_HOLDING.items():
        unit.holding[address] = words
    return unit


@pytest.fixture
def mock_modbus_unit_heat_pump(
    mock_modbus_connection: MockModbusConnection,
) -> MockModbusUnit:
    """A seeded aerosmart heat pump unit (Modbus unit 2)."""
    unit = mock_modbus_connection.for_unit(UNIT_HEAT_PUMP)
    for address, words in HEAT_PUMP_HOLDING.items():
        unit.holding[address] = words
    return unit


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Prevent the created entry from actually setting up during flow tests."""
    with patch(
        "custom_components.aerosmart.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture(autouse=True)
def mock_connection_factory(
    mock_modbus_connection: MockModbusConnection,
) -> Generator[MagicMock]:
    """Route every integration-owned connection through the in-memory mock.

    ``close`` is replaced with a no-op spy so config-entry reload tests can
    reuse the same in-memory register store while still verifying ownership.
    """
    mock_modbus_connection.connect = AsyncMock()  # type: ignore[attr-defined]
    mock_modbus_connection.close = AsyncMock()  # type: ignore[method-assign]
    factory = MagicMock(return_value=mock_modbus_connection)
    with patch("custom_components.aerosmart.connection.create_tcp_connection", factory):
        yield factory


@pytest.fixture
def mock_config_entry(
    mock_modbus_unit_ventilation: MockModbusUnit,
    mock_modbus_unit_heat_pump: MockModbusUnit,
) -> MockConfigEntry:
    """An aerosmart config entry that owns its TCP connection."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="aerosmart",
        unique_id="1.2.3.4:502_1_2",
        version=2,
        data={
            CONF_HOST: "1.2.3.4",
            CONF_PORT: 502,
            CONF_UNIT_VENTILATION: UNIT_VENTILATION,
            CONF_UNIT_HEAT_PUMP: UNIT_HEAT_PUMP,
        },
    )
