"""The aerosmart integration."""

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from . import connection as connection_api
from .aerosmart_modbus import AerosmartDevice
from .const import (
    CONF_UNIT_HEAT_PUMP,
    CONF_UNIT_VENTILATION,
    DEFAULT_PORT,
    LEGACY_CONF_CONNECTION,
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
    connection = connection_api.create_tcp_connection(
        entry.data[CONF_HOST], entry.data[CONF_PORT]
    )
    setup_complete = False
    try:
        await connection.connect()
        unit_ventilation = connection.for_unit(entry.data[CONF_UNIT_VENTILATION])
        unit_heat_pump = connection.for_unit(entry.data[CONF_UNIT_HEAT_PUMP])
        device = AerosmartDevice(unit_ventilation, unit_heat_pump)
        coordinator = AerosmartCoordinator(hass, entry, device, connection)
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        setup_complete = True
        return True
    finally:
        if not setup_complete:
            await connection.close()


async def async_unload_entry(hass: HomeAssistant, entry: AerosmartConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.connection.close()
    return unload_ok


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
