"""unit tests for Modbus write operations"""

import pytest

from modscanner.models import TcpTarget
from modscanner.transports.base import (
    OperationErrorKind,
    WriteResult,
)
from modscanner.writer import Writer

class SuccessfulWriteTransport:
    """fake transport that records successful write operations"""

    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def write_coil(
        self,
        address: int,
        value: bool,
        device_id: int,
    ) -> WriteResult:
        self.calls.append(
            ("write_coil", address, value, device_id)
        )

        return WriteResult.success()

    def write_coils(
        self,
        address: int,
        values: tuple[bool, ...],
        device_id: int,
    ) -> WriteResult:
        self.calls.append(
            ("write_coils", address, values, device_id)
        )

        return WriteResult.success()

    def write_register(
        self,
        address: int,
        value: int,
        device_id: int,
    ) -> WriteResult:
        self.calls.append(
            ("write_register", address, value, device_id)
        )

        return WriteResult.success()

    def write_registers(
        self,
        address: int,
        values: tuple[int, ...],
        device_id: int,
    ) -> WriteResult:
        self.calls.append(
            ("write_registers", address, values, device_id)
        )

        return WriteResult.success()

class FailedWriteTransport:
    """fake transport that fails all write operations"""

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def write_coil(
        self,
        address: int,
        value: bool,
        device_id: int,
    ) -> WriteResult:
        return WriteResult.failure(
            OperationErrorKind.TRANSPORT,
            "Connection timed out",
        )

    def write_coils(
        self,
        address: int,
        values: tuple[bool, ...],
        device_id: int,
    ) -> WriteResult:
        return WriteResult.failure(
            OperationErrorKind.TRANSPORT,
            "Connection timed out",
        )

    def write_register(
        self,
        address: int,
        value: int,
        device_id: int,
    ) -> WriteResult:
        return WriteResult.failure(
            OperationErrorKind.TRANSPORT,
            "Connection timed out",
        )

    def write_registers(
        self,
        address: int,
        values: tuple[int, ...],
        device_id: int,
    ) -> WriteResult:
        return WriteResult.failure(
            OperationErrorKind.TRANSPORT,
            "Connection timed out",
        )

def test_write_single_coil() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    result = writer.write_coil(
        address=5,
        value=True,
    )

    assert result.ok

    assert transport.calls == [
        ("write_coil", 5, True, 1)
    ]

def test_write_multiple_coils() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=2,
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    result = writer.write_coils(
        address=10,
        values=(True, False, True, False),
    )

    assert result.ok

    assert transport.calls == [
        (
            "write_coils",
            10,
            (True, False, True, False),
            2,
        )
    ]

def test_write_single_register() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    result = writer.write_register(
        address=108,
        value=100,
    )

    assert result.ok

    assert transport.calls == [
        ("write_register", 108, 100, 1)
    ]


def test_write_multiple_registers() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=3,
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    result = writer.write_registers(
        address=200,
        values=(10, 20, 30, 40),
    )

    assert result.ok

    assert transport.calls == [
        (
            "write_registers",
            200,
            (10, 20, 30, 40),
            3,
        )
    ]

def test_invalid_register_value_is_rejected() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    with pytest.raises(ValueError):
        writer.write_register(
            address=10,
            value=70_000,
        )

def test_negative_register_value_is_rejected() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    with pytest.raises(ValueError):
        writer.write_register(
            address=10,
            value=-1,
        )

def test_invalid_address_is_rejected() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    with pytest.raises(ValueError):
        writer.write_coil(
            address=70_000,
            value=True,
        )

def test_empty_coil_sequence_is_rejected() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    with pytest.raises(ValueError):
        writer.write_coils(
            address=0,
            values=(),
        )

def test_empty_register_sequence_is_rejected() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = SuccessfulWriteTransport()
    writer = Writer(transport, target)

    with pytest.raises(ValueError):
        writer.write_registers(
            address=0,
            values=(),
        )

def test_transport_error_is_returned_to_writer() -> None:
    target = TcpTarget(
        host="127.0.0.1",
    )

    transport = FailedWriteTransport()
    writer = Writer(transport, target)

    result = writer.write_register(
        address=108,
        value=100,
    )

    assert not result.ok
    assert result.error_kind is OperationErrorKind.TRANSPORT
    assert result.error == "Connection timed out"