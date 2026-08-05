"""DataUpdateCoordinator for aerosmart."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusConnection, ModbusError

from .aerosmart_modbus import AerosmartDevice
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

type AerosmartConfigEntry = ConfigEntry[AerosmartCoordinator]


class AerosmartCoordinator(DataUpdateCoordinator[AerosmartDevice]):
    """Refreshes both aerosmart units on a schedule.

    ``AerosmartDevice.async_update`` fans out to each unit's pooled component
    group, so adding/removing entities never changes what is polled.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: AerosmartConfigEntry,
        device: AerosmartDevice,
        connection: ModbusConnection,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.device = device
        self.connection = connection

    async def _async_update_data(self) -> AerosmartDevice:
        """Fetch the latest data from both aerosmart units."""
        try:
            if not self.connection.connected:
                await self.connection.connect()
            await self.device.async_update()
        except ModbusError as err:
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="update_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        return self.device
