"""read-only Modbus register scanning logic"""

from collections.abc import Callable
from modscanner.models import (
    RegisterArea,
    RegisterResult,
    ResultStatus,
    ScanPlan,
    ScanReport,
    TcpTarget,
)
from modscanner.transports.base import (
    BlockRead,
    ModbusTransport,
    OperationErrorKind,
)

class Scanner:
    """scan Modbus data areas"""

    def __init__(
        self,
        transport: ModbusTransport,
        target: TcpTarget,
    ) -> None:
        self._transport = transport
        self._target = target

    def scan(self, plan: ScanPlan) -> ScanReport:
        """scan the area specified in the scan plan"""

        if plan.area is RegisterArea.COIL:
            return self.scan_coils(plan)

        if plan.area is RegisterArea.DISCRETE_INPUT:
            return self.scan_discrete_inputs(plan)

        if plan.area is RegisterArea.INPUT_REGISTER:
            return self.scan_input_registers(plan)

        if plan.area is RegisterArea.HOLDING_REGISTER:
            return self.scan_holding_registers(plan)

        raise ValueError(
            f"unsupported register area: {plan.area}"
        )

    def scan_coils(
        self,
        plan: ScanPlan,
    ) -> ScanReport:
        """scan coils using function code 01"""

        return self._scan_area(
            plan=plan,
            area=RegisterArea.COIL,
            read_function=self._transport.read_coils,
        )

    def scan_discrete_inputs(
        self,
        plan: ScanPlan,
    ) -> ScanReport:
        """scan discrete inputs using function code 02"""

        return self._scan_area(
            plan=plan,
            area=RegisterArea.DISCRETE_INPUT,
            read_function=self._transport.read_discrete_inputs,
        )

    def scan_input_registers(
        self,
        plan: ScanPlan,
    ) -> ScanReport:
        """scan input registers using function code 04"""

        return self._scan_area(
            plan=plan,
            area=RegisterArea.INPUT_REGISTER,
            read_function=self._transport.read_input_registers,
        )

    def scan_holding_registers(
        self,
        plan: ScanPlan,
    ) -> ScanReport:
        """scan holding registers using function code 03"""

        return self._scan_area(
            plan=plan,
            area=RegisterArea.HOLDING_REGISTER,
            read_function=self._transport.read_holding_registers,
        )

    def _scan_area(
        self,
        plan: ScanPlan,
        area: RegisterArea,
        read_function: Callable[[int, int, int], BlockRead],
    ) -> ScanReport:
        """scan one Modbus data area using adaptive block splitting"""

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
                area=area,
                read_function=read_function,
                results=results,
            )

            current_address += block_count

        results.sort(
            key=lambda result: result.address
        )

        return ScanReport(
            target=self._target,
            plan=plan,
            results=tuple(results),
        )

    def _scan_block(
        self,
        address: int,
        count: int,
        area: RegisterArea,
        read_function: Callable[[int, int, int], BlockRead],
        results: list[RegisterResult],
    ) -> None:
        block = read_function(
            address,
            count,
            self._target.device_id,
        )

        if block.ok:
            values = block.values

            if values is None or len(values) != count:
                self._append_failures(
                    address=address,
                    count=count,
                    area=area,
                    status=ResultStatus.INVALID_RESPONSE,
                    error="transport returned an invalid successful result",
                    results=results,
                )
                return

            for offset, value in enumerate(values):
                results.append(
                    RegisterResult(
                        address=address + offset,
                        area=area,
                        status=ResultStatus.OK,
                        value=value,
                    )
                )

            return

        if (
            block.error_kind is OperationErrorKind.PROTOCOL
            and count > 1
        ):
            left_count = count // 2
            right_count = count - left_count

            self._scan_block(
                address=address,
                count=left_count,
                area=area,
                read_function=read_function,
                results=results,
            )

            self._scan_block(
                address=address + left_count,
                count=right_count,
                area=area,
                read_function=read_function,
                results=results,
            )

            return

        status = self._status_from_error_kind(
            block.error_kind
        )

        self._append_failures(
            address=address,
            count=count,
            area=area,
            status=status,
            error=block.error or "unknown Modbus error",
            results=results,
        )

    @staticmethod
    def _status_from_error_kind(
        error_kind: OperationErrorKind | None,
    ) -> ResultStatus:
        if error_kind is OperationErrorKind.PROTOCOL:
            return ResultStatus.PROTOCOL_ERROR

        if error_kind is OperationErrorKind.TRANSPORT:
            return ResultStatus.TRANSPORT_ERROR

        return ResultStatus.INVALID_RESPONSE

    @staticmethod
    def _append_failures(
        address: int,
        count: int,
        area: RegisterArea,
        status: ResultStatus,
        error: str,
        results: list[RegisterResult],
    ) -> None:
        for offset in range(count):
            results.append(
                RegisterResult(
                    address=address + offset,
                    area=area,
                    status=status,
                    error=error,
                )
            )