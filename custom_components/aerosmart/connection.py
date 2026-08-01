"""Modbus transport owned by the aerosmart integration."""

from modbus_connection import ModbusConnection, ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection as TModbusConnection


def create_tcp_connection(host: str, port: int) -> ModbusConnection:
    """Create a lazy, reconnecting Modbus TCP connection.

    Constructing the connection performs no I/O. The first unit request opens
    the link, and a later request reconnects automatically after a link loss.
    The integration remains the sole owner and closes it during entry unload.
    """
    return TModbusConnection(ModbusTcpParams(host=host, port=port))
