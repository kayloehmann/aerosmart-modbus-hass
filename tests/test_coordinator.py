"""Tests for the aerosmart coordinator."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusConnectionError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _raise_connection_error() -> int:
    """A holding-register value spec that fails every read of its unit."""
    raise ModbusConnectionError("simulated read failure")


async def test_update_failed_marks_entities_unavailable(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit_ventilation: MockModbusUnit,
) -> None:
    """A Modbus read failure fails the update and makes entities unavailable.

    ``mock_modbus_unit_ventilation`` is the same ``MockModbusUnit`` instance
    the coordinator's ``AerosmartDevice`` was built from (both resolve
    through the same ``mock_modbus_connection``), so mutating its store here
    affects the very unit the integration under test reads.
    """
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED

    coordinator = mock_config_entry.runtime_data
    assert coordinator.last_update_success is True

    mock_modbus_unit_ventilation.holding[999_999] = _raise_connection_error

    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success is False
    wochentag = hass.states.get("sensor.aerosmart_wochentag")
    assert wochentag is not None
    assert wochentag.state == STATE_UNAVAILABLE


async def test_recovers_after_transient_failure(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_unit_ventilation: MockModbusUnit,
) -> None:
    """A subsequent successful poll clears the failure again."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    coordinator = mock_config_entry.runtime_data
    mock_modbus_unit_ventilation.holding[999_999] = _raise_connection_error
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert coordinator.last_update_success is False

    del mock_modbus_unit_ventilation.holding[999_999]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success is True
    wochentag = hass.states.get("sensor.aerosmart_wochentag")
    assert wochentag.state == "3"


async def test_reconnects_before_refresh_after_connection_loss(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """A later refresh reconnects a dropped transport before reading."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    async def reconnect() -> None:
        mock_modbus_connection._connected = True  # noqa: SLF001

    mock_modbus_connection.connect.reset_mock()
    mock_modbus_connection.connect.side_effect = reconnect
    mock_modbus_connection.simulate_connection_lost()

    coordinator = mock_config_entry.runtime_data
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    mock_modbus_connection.connect.assert_awaited_once()
    assert coordinator.last_update_success is True
