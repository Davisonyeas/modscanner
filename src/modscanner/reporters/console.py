"""Rich terminal output for ModScanner reports."""

from rich.console import Console
from rich.table import Table
from modscanner.models import RegisterArea, ScanReport

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