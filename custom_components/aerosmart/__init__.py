"""The aerosmart integration."""

from homeassistant.components.modbus import async_get_unit
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from modbus_connection import ModbusTcpParams

from .aerosmart_modbus import AerosmartDevice
from .const import (
    CONF_UNIT_HEAT_PUMP,
    CONF_UNIT_VENTILATION,
    DEFAULT_PORT,
    LEGACY_CONF_CONNECTION,
    MESSAGE_SPACING_SECONDS,
)
from .coordinator import AerosmartConfigEntry, AerosmartCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: AerosmartConfigEntry) -> bool:
    """Set up aerosmart from a config entry."""
    params = ModbusTcpParams(host=entry.data[CONF_HOST], port=entry.data[CONF_PORT])
    unit_ventilation = async_get_unit(
        hass, entry, params, entry.data[CONF_UNIT_VENTILATION]
    )
    unit_heat_pump = async_get_unit(
        hass, entry, params, entry.data[CONF_UNIT_HEAT_PUMP]
    )
    unit_ventilation.set_message_spacing(MESSAGE_SPACING_SECONDS)
    unit_heat_pump.set_message_spacing(MESSAGE_SPACING_SECONDS)
    device = AerosmartDevice(unit_ventilation, unit_heat_pump)
    coordinator = AerosmartCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AerosmartConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: AerosmartConfigEntry) -> bool:
    """Migrate entries that referenced the withdrawn shared-connection integration."""
    if entry.version != 1 or LEGACY_CONF_CONNECTION not in entry.data:
        return True

    legacy_entry = hass.config_entries.async_get_entry(
        entry.data[LEGACY_CONF_CONNECTION]
    )
    if legacy_entry is None or CONF_HOST not in legacy_entry.data:
        return False

    host = str(legacy_entry.data[CONF_HOST])
    port = int(legacy_entry.data.get(CONF_PORT, DEFAULT_PORT))
    data = {
        CONF_HOST: host,
        CONF_PORT: port,
        CONF_UNIT_VENTILATION: int(entry.data[CONF_UNIT_VENTILATION]),
        CONF_UNIT_HEAT_PUMP: int(entry.data[CONF_UNIT_HEAT_PUMP]),
    }
    hass.config_entries.async_update_entry(
        entry,
        data=data,
        unique_id=f"{host.lower()}:{port}_{data[CONF_UNIT_VENTILATION]}_{data[CONF_UNIT_HEAT_PUMP]}",
        version=2,
    )
    return True
