"""Tests for aerosmart-specific Modbus model constraints."""

from modbus_connection.mock import MockModbusConnection

from custom_components.aerosmart.aerosmart_modbus import AerosmartDevice
from custom_components.aerosmart.aerosmart_modbus.aerosmart import (
    ALL_COMPONENTS,
    READING_COMPONENTS,
    SETTINGS_COMPONENTS,
)


def test_read_plan_never_combines_datapoints() -> None:
    """Real controllers only accept one 32-bit datapoint per request."""
    connection = MockModbusConnection()
    device = AerosmartDevice(connection.for_unit(1), connection.for_unit(2))

    for component_name in ALL_COMPONENTS:
        component = getattr(device, component_name)
        for blocks in component._build_plan().blocks.values():
            assert all(count <= 2 for _address, count in blocks)


def test_poll_categories_partition_the_register_map() -> None:
    """The fast and slow polls cover every field exactly once."""
    connection = MockModbusConnection()
    device = AerosmartDevice(connection.for_unit(1), connection.for_unit(2))

    def request_count(names: tuple[str, ...]) -> int:
        return sum(
            len(blocks)
            for name in names
            for blocks in getattr(device, name)._build_plan().blocks.values()
        )

    assert set(READING_COMPONENTS).isdisjoint(SETTINGS_COMPONENTS)
    assert set(ALL_COMPONENTS) == set(READING_COMPONENTS) | set(SETTINGS_COMPONENTS)
    assert request_count(READING_COMPONENTS) == 115
    assert request_count(SETTINGS_COMPONENTS) == 22
