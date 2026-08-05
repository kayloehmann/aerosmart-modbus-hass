"""Tests for aerosmart-specific Modbus model constraints."""

from modbus_connection.mock import MockModbusConnection

from custom_components.aerosmart.aerosmart_modbus import AerosmartDevice


def test_read_plan_never_combines_datapoints() -> None:
    """Real controllers only accept one 32-bit datapoint per request."""
    connection = MockModbusConnection()
    device = AerosmartDevice(connection.for_unit(1), connection.for_unit(2))

    for group in (device._group_ventilation, device._group_heat_pump):
        for blocks in group._build_plan().blocks.values():
            assert all(count <= 2 for _address, count in blocks)
