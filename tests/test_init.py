"""Tests for the aerosmart config-entry setup."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from modbus_connection.mock import MockModbusConnection
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_setup_entry_creates_entities(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """The entry loads and produces entities across every platform."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.LOADED
    mock_modbus_connection.connect.assert_awaited_once()

    wochentag = hass.states.get("sensor.aerosmart_wochentag")
    assert wochentag is not None
    assert wochentag.state == "3"

    outside_temp = hass.states.get("sensor.aerosmart_temperatur_aussenluft")
    assert outside_temp is not None
    assert outside_temp.state == "0.123"


async def test_unload_closes_owned_connection(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_modbus_connection: MockModbusConnection,
) -> None:
    """Unloading the entry permanently closes its owned connection."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)

    mock_modbus_connection.close.assert_awaited_once()


async def test_migrates_legacy_shared_connection_entry(hass: HomeAssistant) -> None:
    """Version 1 entries copy host and port from their former connection entry."""
    legacy_connection = MockConfigEntry(
        domain="modbus_connection",
        data={CONF_HOST: "gateway.local", CONF_PORT: 8899},
    )
    legacy_connection.add_to_hass(hass)
    entry = MockConfigEntry(
        domain="aerosmart",
        version=1,
        data={
            "connection_entry_id": legacy_connection.entry_id,
            "unit_ventilation": 1,
            "unit_heat_pump": 2,
        },
    )
    entry.add_to_hass(hass)

    from custom_components.aerosmart import async_migrate_entry

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.unique_id == "gateway.local:8899_1_2"
    assert entry.data == {
        CONF_HOST: "gateway.local",
        CONF_PORT: 8899,
        "unit_ventilation": 1,
        "unit_heat_pump": 2,
    }
