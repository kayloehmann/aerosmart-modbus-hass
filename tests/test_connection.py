"""Tests for the integration-owned Modbus transport."""

from unittest.mock import patch

from modbus_connection import ModbusTcpParams

from custom_components.aerosmart.connection import create_tcp_connection
from custom_components.aerosmart.const import MESSAGE_SPACING_SECONDS


def test_connection_uses_connection_wide_message_spacing() -> None:
    """Pace requests across station changes, not only within one station."""
    with patch(
        "custom_components.aerosmart.connection.TModbusConnection"
    ) as constructor:
        create_tcp_connection("gateway.local", 8899)

    constructor.assert_called_once_with(
        ModbusTcpParams(host="gateway.local", port=8899),
        message_spacing=MESSAGE_SPACING_SECONDS,
    )
