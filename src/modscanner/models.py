"""Core data models used by ModScanner."""

from dataclasses import dataclass
from enum import StrEnum

class RegisterArea(StrEnum):
    """supported Modbus data areas"""

    COIL = "coil"
    DISCRETE_INPUT = "discrete_input"
    INPUT_REGISTER = "input_register"
    HOLDING_REGISTER = "holding_register"

class ResultStatus(StrEnum):
    """outcome of reading an individual Modbus address"""

    OK = "ok"
    PROTOCOL_ERROR = "protocol_error"
    TRANSPORT_ERROR = "transport_error"
    INVALID_RESPONSE = "invalid_response"

@dataclass(frozen=True, slots=True)
class TcpTarget:
    """connection information for a Modbus TCP device"""

    host: str
    port: int = 502
    device_id: int = 1
    timeout: float = 3.0

    def __post_init__(self) -> None:
        """validate Modbus TCP target configuration"""

        if not self.host.strip():
            raise ValueError("host cannot be empty")

        if not 1 <= self.port <= 65_535:
            raise ValueError(
                "port must be between 1 and 65535"
            )

        if not 0 <= self.device_id <= 247:
            raise ValueError(
                "device_id must be between 0 and 247"
            )

        if self.timeout <= 0:
            raise ValueError(
                "timeout must be greater than zero"
            )

@dataclass(frozen=True, slots=True)
class ScanPlan:
    """description of a contiguous Modbus data-area scan"""

    start: int
    count: int
    block_size: int = 125
    area: RegisterArea = RegisterArea.HOLDING_REGISTER

    def __post_init__(self) -> None:
        """validate the scan plan"""

        if not 0 <= self.start <= 65_535:
            raise ValueError(
                "start must be between 0 and 65535"
            )

        if self.count < 1:
            raise ValueError(
                "count must be at least 1"
            )

        if self.start + self.count > 65_536:
            raise ValueError(
                "the requested address range exceeds 65535"
            )

        if not 1 <= self.block_size <= 125:
            raise ValueError(
                "block_size must be between 1 and 125"
            )

@dataclass(frozen=True, slots=True)
class RegisterResult:
    """result for one scanned Modbus register"""

    address: int
    area: RegisterArea
    status: ResultStatus
    value: int | None = None
    error: str | None = None

@dataclass(frozen=True, slots=True)
class ScanReport:
    """complete result of a Modbus register scan"""

    target: TcpTarget
    plan: ScanPlan
    results: tuple[RegisterResult, ...]

    @property
    def successful_count(self) -> int:
        """return the number of successfully read registers"""

        return sum(
            result.status is ResultStatus.OK
            for result in self.results
        )

    @property
    def failed_count(self) -> int:
        """return the number of registers that could not be read"""

        return len(self.results) - self.successful_count