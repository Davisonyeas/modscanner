'''read-only Modbus register scanning logic'''

from modscanner.models import (
    RegisterArea,
    RegisterResult,
    ResultStatus,
    ScanPlan,
    ScanReport,
    TcpTarget,
)
from modscanner.transports.base import (
    ModbusTransport,
    ReadErrorKind,
)


class Scanner:
    '''read-only Modbus scanner'''

    def __init__(
        self,
        transport: ModbusTransport,
        target: TcpTarget,
    ) -> None:
        self._transport = transport
        self._target = target

    def scan_holding_registers(self, plan: ScanPlan) -> ScanReport:
        '''scan holding registers using adaptive block splitting'''

        results: list[RegisterResult] = []

        range_end = plan.start + plan.count
        current_address = plan.start

        while current_address < range_end:
            block_count = min(
                plan.block_size,
                range_end - current_address,
            )

            self._scan_block(
                address=current_address,
                count=block_count,
                results=results,
            )

            current_address += block_count

        results.sort(key=lambda result: result.address)

        return ScanReport(
            target=self._target,
            plan=plan,
            results=tuple(results),
        )

    def _scan_block(
        self,
        address: int,
        count: int,
        results: list[RegisterResult],
    ) -> None:
        block = self._transport.read_holding_registers(
            address=address,
            count=count,
            device_id=self._target.device_id,
        )

        if block.ok:
            values = block.values

            if values is None or len(values) != count:
                self._append_failures(
                    address=address,
                    count=count,
                    status=ResultStatus.INVALID_RESPONSE,
                    error="transport returned an invalid successful result",
                    results=results,
                )
                return

            for offset, value in enumerate(values):
                results.append(
                    RegisterResult(
                        address=address + offset,
                        area=RegisterArea.HOLDING_REGISTER,
                        status=ResultStatus.OK,
                        value=value,
                    )
                )

            return

        if block.error_kind is ReadErrorKind.PROTOCOL and count > 1:
            left_count = count // 2
            right_count = count - left_count

            self._scan_block(
                address=address,
                count=left_count,
                results=results,
            )

            self._scan_block(
                address=address + left_count,
                count=right_count,
                results=results,
            )

            return

        status = self._status_from_error_kind(block.error_kind)

        self._append_failures(
            address=address,
            count=count,
            status=status,
            error=block.error or "unknown Modbus error",
            results=results,
        )

    @staticmethod
    def _status_from_error_kind(
        error_kind: ReadErrorKind | None,
    ) -> ResultStatus:
        if error_kind is ReadErrorKind.PROTOCOL:
            return ResultStatus.PROTOCOL_ERROR

        if error_kind is ReadErrorKind.TRANSPORT:
            return ResultStatus.TRANSPORT_ERROR

        return ResultStatus.INVALID_RESPONSE

    @staticmethod
    def _append_failures(
        address: int,
        count: int,
        status: ResultStatus,
        error: str,
        results: list[RegisterResult],
    ) -> None:
        for offset in range(count):
            results.append(
                RegisterResult(
                    address=address + offset,
                    area=RegisterArea.HOLDING_REGISTER,
                    status=status,
                    error=error,
                )
            )