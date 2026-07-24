'''core data models used by modscanner'''

from enum import StrEnum
from dataclasses import dataclass

class RegisterArea(StrEnum):
    '''supported modbus data areas'''

    HOLDING_REGISTER = "holding"

class ResultStatus(StrEnum):
    '''outcome  of reading individual modbus addresss'''

    OK = "ok"
    PROTOCOL_ERROR = "transport_error"
    TRANSPORT_ERROR = "transport_error"
    INVALID_RESPONSE = "invalid_response"

@dataclass(frozen=True, slots=True)
class TcpTarget:
    '''commection information for a modbus tcp device'''

    host: str
    port: int = 502
    device_id: int = 1
    timeout: float = 3.0

    def post_init__(self) -> None:
        if not 0 <= self.start <= 65_535:
            raise ValueError("start must be between 0 and 65535")

        if self.count < 1:
            raise ValueError("count must be at least 1")

        if self.start + self.count > 65_536:
            raise ValueError("the requested address range exceeds 65535")

        if not 1 <= self.block_size <= 125:
            raise ValueError("block_size must be between 1 and 125")


@dataclass(frozen=True, slots=True)
class ScanPlan:
    '''description og contiguous holding register scan'''

    start: int
    count: int
    block_size: int = 125

    def __post_init__(self) -> None:
        if not 0 <= self.start <= 65_535:
            raise ValueError("start must be between 0 and 65535")

        if self.count < 1:
            raise ValueError("count must be atleast 1")

        if self.start + self.count > 65_536:
            raise ValueError("the requested address range exceeeds 65535")

        if not 1 <= self.block_size <= 125:
            raise ValueError("block size must be between 1 and 125")

@dataclass(frozen=True, slots=True)
class RegisterResult:
    '''result for one scanned Modbus register'''

    address: int
    area: RegisterArea
    status: ResultStatus
    value: int | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class ScanReport:
    '''complete result of a Modbus register scan'''

    target: TcpTarget
    plan: ScanPlan
    results: tuple[RegisterResult, ...]

    @property
    def successful_count(self) -> int:
        '''return the number of successfully read registers'''

        return sum(result.status is ResultStatus.OK for result in self.results)

    @property
    def failed_count(self) -> int:
        '''return the number of registers that could not be read'''

        return len(self.results) - self.successful_count