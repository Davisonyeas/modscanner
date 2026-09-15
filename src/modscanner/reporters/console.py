"""Rich terminal output for ModScanner reports."""

from rich.console import Console
from rich.table import Table
from modscanner.decoder import decode_registers, registers_per_value
from modscanner.models import (
    DataType,
    RegisterArea,
    ResultStatus,
    ScanReport,
    WordOrder,
)

AREA_NAMES = {
    RegisterArea.COIL: "Coils",
    RegisterArea.DISCRETE_INPUT: "Discrete Inputs",
    RegisterArea.INPUT_REGISTER: "Input Registers",
    RegisterArea.HOLDING_REGISTER: "Holding Registers",
}

def render_report(
    report: ScanReport,
    console: Console | None = None,
) -> None:
    """render a scan report as a terminal table."""

    output = console or Console()

    area_name = AREA_NAMES.get(
        report.plan.area,
        report.plan.area.value,
    )

    table = Table(
        title=(
            f"{area_name}: "
            f"{report.target.host}:{report.target.port} "
            f"(device {report.target.device_id})"
        )
    )

    table.add_column(
        "Address",
        justify="right",
    )

    table.add_column(
        "Value",
        justify="right",
    )

    table.add_column("Status")
    table.add_column("Error")

    for result in report.results:
        table.add_row(
            str(result.address),
            (
                ""
                if result.value is None
                else str(result.value)
            ),
            result.status.value,
            result.error or "",
        )

    output.print(table)

    output.print(
        f"Successful: {report.successful_count} | "
        f"Failed: {report.failed_count}"
    )


def render_typed_report(
    report: ScanReport,
    data_type: DataType,
    word_order: WordOrder = WordOrder.BIG,
    console: Console | None = None,
) -> None:
    """Render a register scan with typed value decoding."""

    output = console or Console()

    if report.plan.area not in {
        RegisterArea.HOLDING_REGISTER,
        RegisterArea.INPUT_REGISTER,
    }:
        raise ValueError(
            "typed decoding is only supported for register areas"
        )

    width = registers_per_value(data_type)

    table = Table(
        title=(
            f"{AREA_NAMES[report.plan.area]}: "
            f"{report.target.host}:{report.target.port} "
            f"(device {report.target.device_id}) "
            f"[{data_type.value}]"
        )
    )

    table.add_column("Address", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Error")

    results = report.results

    for index in range(0, len(results), width):
        group = results[index:index + width]

        address = group[0].address

        if len(group) != width:
            table.add_row(
                str(address),
                "",
                data_type.value,
                "invalid_response",
                (
                    f"{data_type.value} requires "
                    f"{width} register(s)"
                ),
            )
            continue

        failed = next(
            (
                result
                for result in group
                if result.status is not ResultStatus.OK
            ),
            None,
        )

        if failed is not None:
            table.add_row(
                str(address),
                "",
                data_type.value,
                failed.status.value,
                failed.error or "",
            )
            continue

        values = tuple(
            result.value
            for result in group
            if result.value is not None
        )

        if len(values) != width:
            table.add_row(
                str(address),
                "",
                data_type.value,
                "invalid_response",
                "missing register value",
            )
            continue

        try:
            value = decode_registers(
                values,
                data_type,
                word_order,
            )
        except ValueError as exc:
            table.add_row(
                str(address),
                "",
                data_type.value,
                "invalid_response",
                str(exc),
            )
            continue

        table.add_row(
            str(address),
            str(value),
            data_type.value,
            "ok",
            "",
        )

    output.print(table)