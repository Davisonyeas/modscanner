'''rich terminal output for ModScanner reports'''

from rich.console import Console
from rich.table import Table
from modscanner.models import ScanReport

def render_report(
    report: ScanReport,
    console: Console | None = None,
) -> None:
    '''render a scan report as a terminal table'''

    output = console or Console()

    table = Table(
        title=(
            f"Holding registers: "
            f"{report.target.host}:{report.target.port} "
            f"(device {report.target.device_id})"
        )
    )

    table.add_column("Address", justify="right")
    table.add_column("Value", justify="right")
    table.add_column("Status")
    table.add_column("Error")

    for result in report.results:
        table.add_row(
            str(result.address),
            "" if result.value is None else str(result.value),
            result.status.value,
            result.error or "",
        )

    output.print(table)
    output.print(
        f"Successful: {report.successful_count} | "
        f"Failed: {report.failed_count}"
    )