"""unit tests for adaptive holding-register scanning"""

from modscanner.models import (
    ResultStatus,
    ScanPlan,
    TcpTarget,
)
from modscanner.scanner import Scanner
from modscanner.transports.base import (
    BlockRead,
    OperationErrorKind,
)


class SparseRegisterTransport:
    """fake transport where only addresses 8 and 9 are valid"""

    def __init__(self) -> None:
        self.calls: list[tuple[int, int, int]] = []

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read_holding_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        self.calls.append((address, count, device_id))

        if address >= 8 and address + count <= 10:
            values = tuple(
                1_000 + current for current in range(address, address + count)
            )
            return BlockRead.success(values)

        return BlockRead.failure(
            OperationErrorKind.PROTOCOL,
            "Illegal data address",
        )


class FailedTransport:
    """fake transport representing an unavailable connection"""

    def __init__(self) -> None:
        self.call_count = 0

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def read_holding_registers(
        self,
        address: int,
        count: int,
        device_id: int,
    ) -> BlockRead:
        self.call_count += 1

        return BlockRead.failure(
            OperationErrorKind.TRANSPORT,
            "Connection timed out",
        )

def test_scanner_identifies_valid_addresses_inside_rejected_block() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )
    plan = ScanPlan(
        start=8,
        count=5,
        block_size=5,
    )
    transport = SparseRegisterTransport()
    scanner = Scanner(transport, target)

    report = scanner.scan_holding_registers(plan)

    assert len(report.results) == 5
    assert report.successful_count == 2
    assert report.failed_count == 3

    assert report.results[0].address == 8
    assert report.results[0].value == 1_008
    assert report.results[0].status is ResultStatus.OK

    assert report.results[1].address == 9
    assert report.results[1].value == 1_009
    assert report.results[1].status is ResultStatus.OK

    assert all(
        result.status is ResultStatus.PROTOCOL_ERROR for result in report.results[2:]
    )

    assert len(transport.calls) > 1


def test_transport_error_does_not_trigger_recursive_requests() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )
    plan = ScanPlan(
        start=0,
        count=20,
        block_size=20,
    )
    transport = FailedTransport()
    scanner = Scanner(transport, target)

    report = scanner.scan_holding_registers(plan)

    assert transport.call_count == 1
    assert report.successful_count == 0
    assert report.failed_count == 20

    assert all(
        result.status is ResultStatus.TRANSPORT_ERROR for result in report.results
    )
