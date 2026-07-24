'''transport abstraction used by the ModScanner core'''

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

class ReadErrorKind(StrEnum):
    '''categories of errors returned by a transport'''

    PROTOCOL = "protocol"
    TRANSPORT = "transport"
    INVALID_RESPONSE = "invalid_response"

@dataclass(frozen=True, slots=True)
class BlockRead:
    '''result of reading one contiguous block of rgisters'''

    values: tuple[int, ...] | None = None
    error_kind: ReadErrorKind | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        '''return whether the operation wass a success'''

        return self.error_kind is None

    @classmethod
    def success(cls, values: tuple[int, ...]) -> "BlockRead":
        '''create a successful block result'''

        return cls(values=values)

    @classmethod
    def failure (
        cls,
        kind: ReadErrorKind,
        error: str,
    ) -> "BlockRead":
        '''create a failed block result'''

        return cls(
            error_kind=kind, 
            error=error
        )

class ModbusTransport(Protocol):
    '''interface implemented by concret Modbus transports'''

    def connect(self) -> None:
        '''connect to the Modbus device'''

    def close(self) -> None:
        '''close the connection'''

    def read_holding_registers(
            self,
            address: int,
            count: int, 
            device_id: int,
    ) -> BlockRead:
        '''read a contiguoous block of holding registers'''