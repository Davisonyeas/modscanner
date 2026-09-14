"""PyModbus-backed Modbus TCP transport."""

from typing import Any
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
from modscanner.exceptions import ModScannerConnectionError
from modscanner.models import TcpTarget
from modscanner.transports.base import (
    BlockRead,
    OperationErrorKind,
    WriteResult,
)

class PymodbusTcpTransport:
    """synchronous Modbus TCP transport using PyModbus"""

    def __init__(self, target: TcpTarget) -> None:
        self._target = target

        self._client = ModbusTcpClient(
            host=target.host,
            port=target.port,
            timeout=target.timeout,
        )

    def connect(self) -> None:
        """connect to the configured Modbus TCP device"""

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
        """close the Modbus TCP connection"""

        self._client.close()

    def read_device_information(
        self,
        device_id: int,
    ) -> str | None:
        """attempt to read basic Modbus device information"""

        try:
            response = self._client.read_device_information(
                read_code=1,
                object_id=0,
                device_id=device_id,
            )

            if not response.isError():
                information = getattr(response, "information", None)

                if information:
                    manufacturer = information.get(0)

                    if manufacturer is not None:
                        if isinstance(manufacturer, bytes):
                            return manufacturer.decode(
                                "utf-8",
                                errors="ignore",
                            )

                        return str(manufacturer)

                return "Active Modbus Device"

        except (ModbusException, OSError, TimeoutError):
            pass

        try:
            response = self._client.read_holding_registers(
                address=0,
                count=1,
                device_id=device_id,
            )

            if response is not None and not response.isError():
                return "Active Modbus Device Identity Hidden"

        except (ModbusException, OSError, TimeoutError):
            pass

        return None

    def read_coils(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read coils using function code 01"""

        try:
            response = self._client.read_coils(
                address=address,
                count=count,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return BlockRead.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        if response is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return BlockRead.failure(
                OperationErrorKind.PROTOCOL,
                str(response),
            )

        bits = getattr(response, "bits", None)

        if bits is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the response did not contain coil values",
            )

        values = tuple(
            int(value)
            for value in bits[:count]
        )

        if len(values) != count:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                f"expected {count} coils but received {len(values)}",
            )

        return BlockRead.success(values)

    def read_discrete_inputs(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read discrete inputs using function code 02"""

        try:
            response = self._client.read_discrete_inputs(
                address=address,
                count=count,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return BlockRead.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        if response is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return BlockRead.failure(
                OperationErrorKind.PROTOCOL,
                str(response),
            )

        bits = getattr(response, "bits", None)

        if bits is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the response did not contain discrete input values",
            )

        values = tuple(
            int(value)
            for value in bits[:count]
        )

        if len(values) != count:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                f"expected {count} discrete inputs but received {len(values)}",
            )

        return BlockRead.success(values)

    def read_input_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read input registers using function code 04"""

        try:
            response = self._client.read_input_registers(
                address=address,
                count=count,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return BlockRead.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        if response is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return BlockRead.failure(
                OperationErrorKind.PROTOCOL,
                str(response),
            )

        registers = getattr(response, "registers", None)

        if registers is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the response did not contain registers",
            )

        values = tuple(
            int(value)
            for value in registers
        )

        if len(values) != count:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                f"expected {count} registers but received {len(values)}",
            )

        return BlockRead.success(values)

    def read_holding_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read holding registers using function code 03"""

        try:
            response = self._client.read_holding_registers(
                address=address,
                count=count,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return BlockRead.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        if response is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return BlockRead.failure(
                OperationErrorKind.PROTOCOL,
                str(response),
            )

        registers = getattr(response, "registers", None)

        if registers is None:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the response did not contain registers",
            )

        values = tuple(int(value) for value in registers)

        if len(values) != count:
            return BlockRead.failure(
                OperationErrorKind.INVALID_RESPONSE,
                f"expected {count} registers but received {len(values)}",
            )

        return BlockRead.success(values)

    def write_coil(
        self,
        address: int,
        value: bool,
        device_id: int,
    ) -> WriteResult:
        """write one coil using function code 05"""

        try:
            response = self._client.write_coil(
                address=address,
                value=value,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return WriteResult.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        return self._handle_write_response(response)

    def write_coils(
        self,
        address: int,
        values: tuple[bool, ...],
        device_id: int,
    ) -> WriteResult:
        """write multiple coils using function code 15"""

        try:
            response = self._client.write_coils(
                address=address,
                values=list(values),
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return WriteResult.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        return self._handle_write_response(response)

    def write_register(
        self,
        address: int,
        value: int,
        device_id: int,
    ) -> WriteResult:
        """write one holding register using function code 06"""

        try:
            response = self._client.write_register(
                address=address,
                value=value,
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return WriteResult.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        return self._handle_write_response(response)

    def write_registers(
        self,
        address: int,
        values: tuple[int, ...],
        device_id: int,
    ) -> WriteResult:
        """write multiple holding registers using function code 16"""

        try:
            response = self._client.write_registers(
                address=address,
                values=list(values),
                device_id=device_id,
            )

        except (ModbusException, OSError, TimeoutError) as exc:
            return WriteResult.failure(
                OperationErrorKind.TRANSPORT,
                str(exc),
            )

        return self._handle_write_response(response)

    @staticmethod
    def _handle_write_response(
        response: Any,
    ) -> WriteResult:
        """convert a PyModbus write response into a WriteResult"""

        if response is None:
            return WriteResult.failure(
                OperationErrorKind.INVALID_RESPONSE,
                "the device returned no response object",
            )

        if response.isError():
            return WriteResult.failure(
                OperationErrorKind.PROTOCOL,
                str(response),
            )

        return WriteResult.success()