'''PyModbus-backed Modbus TCP transport'''

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from modscanner.exceptions import ModScannerConnectionError
from modscanner.models import TcpTarget
from modscanner.transports.base import BlockRead, ReadErrorKind

class PymodbusTcpTransport:
    '''synchronous Modbus TCP transport using PyModbus'''

    def __init__(self, target: TcpTarget) -> None:
        self._target = target
        self._client = ModbusTcpClient(
            host=target.host,
            port=target.port,
            timeout=target.timeout,
        )

    def connect(self) -> None:
        '''connect to the configured Modbus TCP device'''

        try:
            connected = self._client.connect()
        except (ModbusException, OSError, TimeoutError) as exc:
            raise ModScannerConnectionError(
                f"could not connect to "
                f"{self._target.host}:{self._target.port}: {exc}"
            ) from exc

        if not connected:
            raise ModScannerConnectionError(
                f"could not connect to "
                f"{self._target.host}:{self._target.port}"
            )

    def close(self) -> None:
        '''close the PyModbus TCP connection'''

        self._client.close()

    def read_holding_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        '''read holding registers using function code 03'''
    
        try:
            response = self._client.read_holding_registers(
                address,
                count=count,
                device_id=device_id,
            )
        except (ModbusException, OSError, TimeoutError) as exc:
            return BlockRead.failure(
                ReadErrorKind.TRANSPORT,
                str(exc),
            )

        if response is None:
            return BlockRead.failure(
                ReadErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return BlockRead.failure(
                ReadErrorKind.PROTOCOL,
                str(response),
            )

        registers = getattr(response, "registers", None)

        if registers is None:
            return BlockRead.failure(
                ReadErrorKind.INVALID_RESPONSE,
                "the response did not contain registers",
            )

        values = tuple(int(value) for value in registers)

        if len(values) != count:
            return BlockRead.failure(
                ReadErrorKind.INVALID_RESPONSE,
                f"expected {count} registers but received {len(values)}",
            )

        return BlockRead.success(values)