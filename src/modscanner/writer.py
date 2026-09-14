"""Modbus write operations"""

from modscanner.models import TcpTarget
from modscanner.transports.base import (
    ModbusTransport,
    WriteResult,
)

class Writer:
    """perform Modbus write operations"""

    def __init__(
        self,
        transport: ModbusTransport,
        target: TcpTarget,
    ) -> None:
        self._transport = transport
        self._target = target

    def write_coil(
        self,
        address: int,
        value: bool,
    ) -> WriteResult:
        """write one coil using function code 05"""

        self._validate_address(address)

        return self._transport.write_coil(
            address=address,
            value=value,
            device_id=self._target.device_id,
        )

    def write_coils(
        self,
        address: int,
        values: tuple[bool, ...],
    ) -> WriteResult:
        """write multiple coils using function code 15"""

        self._validate_address(address)

        if not values:
            raise ValueError("values cannot be empty")

        if len(values) > 1968:
            raise ValueError(
                "cannot write more than 1968 coils in one request"
            )

        self._validate_range(address, len(values))

        return self._transport.write_coils(
            address=address,
            values=values,
            device_id=self._target.device_id,
        )

    def write_register(
        self,
        address: int,
        value: int,
    ) -> WriteResult:
        """write one holding register using function code 06"""

        self._validate_address(address)
        self._validate_register_value(value)

        return self._transport.write_register(
            address=address,
            value=value,
            device_id=self._target.device_id,
        )

    def write_registers(
        self,
        address: int,
        values: tuple[int, ...],
    ) -> WriteResult:
        """write multiple holding registers using function code 16"""

        self._validate_address(address)

        if not values:
            raise ValueError("values cannot be empty")

        if len(values) > 123:
            raise ValueError(
                "cannot write more than 123 registers in one request"
            )

        self._validate_range(address, len(values))

        for value in values:
            self._validate_register_value(value)

        return self._transport.write_registers(
            address=address,
            values=values,
            device_id=self._target.device_id,
        )

    @staticmethod
    def _validate_address(address: int) -> None:
        if not 0 <= address <= 65_535:
            raise ValueError(
                "address must be between 0 and 65535"
            )

    @staticmethod
    def _validate_range(
        address: int,
        count: int,
    ) -> None:
        if address + count > 65_536:
            raise ValueError(
                "requested address range exceeds 65535"
            )

    @staticmethod
    def _validate_register_value(value: int) -> None:
        if not 0 <= value <= 65_535:
            raise ValueError(
                "register value must be between 0 and 65535"
            )