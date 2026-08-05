"""Modbus transport owned by the aerosmart integration."""

from modbus_connection import ModbusConnection, ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection as TModbusConnection

from .const import MESSAGE_SPACING_SECONDS


def create_tcp_connection(host: str, port: int) -> ModbusConnection:
    """Create a lazy, reconnecting Modbus TCP connection.

    Constructing the connection performs no I/O. The integration remains the
    sole owner: it explicitly connects before the first request, reconnects the
    same object after a link loss, and closes it during entry unload.
    """
    return TModbusConnection(
        ModbusTcpParams(host=host, port=port),
        message_spacing=MESSAGE_SPACING_SECONDS,
    )
