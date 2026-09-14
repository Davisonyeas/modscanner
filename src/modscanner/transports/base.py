"""transport abstraction used by the ModScanner core"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class OperationErrorKind(StrEnum):
    """categories of errors returned by a transport"""

    PROTOCOL = "protocol"
    TRANSPORT = "transport"
    INVALID_RESPONSE = "invalid_response"

@dataclass(frozen=True, slots=True)
class BlockRead:
    """result of reading one contiguous block of rgisters"""

    values: tuple[int, ...] | None = None
    error_kind: OperationErrorKind | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        """return whether the operation wass a success"""

        return self.error_kind is None

    @classmethod
    def success(cls, values: tuple[int, ...]) -> "BlockRead":
        """create a successful block result"""

        return cls(values=values)

    @classmethod
    def failure(
        cls,
        kind: OperationErrorKind,
        error: str,
    ) -> "BlockRead":
        """create a failed block result"""

        return cls(error_kind=kind, error=error)

@dataclass(frozen=True, slots=True)
class WriteResult:
    """result of a Modbus write operation"""

    error_kind: OperationErrorKind | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error_kind is None

    @classmethod
    def success(cls) -> "WriteResult":
        return cls()

    @classmethod
    def failure(
        cls,
        kind: OperationErrorKind,
        error: str,
    ) -> "WriteResult":
        return cls(error_kind=kind, error=error)

class ModbusTransport(Protocol):
    """interface implemented by concrete Modbus transports"""

    def connect(self) -> None:
        """connect to the Modbus device"""

    def close(self) -> None:
        """close the connection"""

    def read_coils(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read coils"""

    def read_discrete_inputs(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read discrete inputs"""

    def read_input_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read input registers"""

    def read_holding_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        """read holding registers"""

    def write_coil(
        self,
        address: int,
        value: bool,
        device_id: int,
    ) -> WriteResult:
        """write one coil using FC05"""

    def write_coils(
        self,
        address: int,
        values: tuple[bool, ...],
        device_id: int,
    ) -> WriteResult:
        """write multiple coils using FC15"""

    def write_register(
        self,
        address: int,
        value: int,
        device_id: int,
    ) -> WriteResult:
        """write one holding register using FC06"""

    def write_registers(
        self,
        address: int,
        values: tuple[int, ...],
        device_id: int,
    ) -> WriteResult:
        """write multiple holding registers using FC16"""