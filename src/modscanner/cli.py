'''command-line interface for ModScanner'''

import typer
from rich.console import Console
from modscanner.exceptions import ModScannerConnectionError
from modscanner.models import ScanPlan, TcpTarget
from modscanner.reporters.console import render_report
from modscanner.scanner import Scanner
from modscanner.transports.pymodbus_transport import (
    PymodbusTcpTransport,
)

app = typer.Typer(
    name="modscanner",
    help="safely discover and inspect Modbus devices via RTU and TCP.",
    no_args_is_help=True,
    context_settings={"help_option_names" : ["--help", "--h", "-help", "--h"]}
)

console = Console()

@app.command("scan-tcp")
def scan_tcp(
    host: str = typer.Argument(
        ...,
        help="hostname or IP address of the Modbus TCP device.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
        help="zero-based starting register address.",
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
        help="number of registers to scan.",
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=1,
        max=247,
        help="Modbus device identifier.",
    ),
    port: int = typer.Option(
        502,
        "--port",
        "-p",
        min=1,
        max=65_535,
        help="Modbus TCP port.",
    ),
    timeout: float = typer.Option(
        3.0,
        "--timeout",
        min=0.1,
        help="Request timeout in seconds.",
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
        help="maximum registers requested per block.",
    ),
) -> None:
    """scan a range of Modbus TCP holding registers."""

    try:
        target = TcpTarget(
            host=host,
            port=port,
            device_id=device_id,
            timeout=timeout,
        )

        plan = ScanPlan(
            start=start,
            count=count,
            block_size=block_size,
        )
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

    transport = PymodbusTcpTransport(target)
    scanner = Scanner(transport, target)

    try:
        transport.connect()
        report = scanner.scan_holding_registers(plan)
    except ModScannerConnectionError as exc:
        console.print(f"Connection failed: {exc}")
        raise typer.Exit(code=2) from exc
    finally:
        transport.close()

    render_report(report, console)

@app.command()
def version() -> None:
    '''display the installed ModScanner version'''

    from modscanner import __version__

    console.print(f"modscanner {__version__}")

if __name__ == "__main__":
    app()