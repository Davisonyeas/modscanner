"""Command-line interface for ModScanner."""

import ipaddress
import os
import socket
import sys
from typing import Any, cast
import nmap
import psutil
import typer
from nmap import PortScannerError, PortScannerTimeout
from rich.console import Console
from rich.table import Table
# from rich.live import Live

from modscanner.exceptions import ModScannerConnectionError
from modscanner.reporters.console import render_report, render_typed_report
from modscanner.scanner import Scanner
from modscanner.transports.base import WriteResult
from modscanner.transports.pymodbus_transport import PymodbusTcpTransport
from modscanner.writer import Writer
from modscanner.models import (
    DataType,
    RegisterArea,
    ScanPlan,
    TcpTarget,
    WordOrder,
)
from modscanner.decoder import registers_per_value

app = typer.Typer(
    name="modscanner",
    help="Discover, inspect, and interact with Modbus TCP devices.",
    no_args_is_help=True,
    context_settings={
        "help_option_names": ["--help", "-h"],
    },
)

scan_app = typer.Typer(
    help="Read and scan Modbus data areas.",
    no_args_is_help=True,
)

write_app = typer.Typer(
    help="Write Modbus coils and holding registers.",
    no_args_is_help=True,
)

app.add_typer(scan_app, name="scan")
app.add_typer(write_app, name="write")

DEFAULT_PORT = 502
DEFAULT_TIMEOUT = 3.0
NETWORK_SCAN_TIMEOUT = 0.5

console = Console()
nm = nmap.PortScanner()


# SHARED HELPERS

def _render_write_result(
    result: WriteResult,
    target: TcpTarget,
) -> None:
    """render a Modbus write result."""

    if result.ok:
        console.print(
            f"[green]Write successful[/green] "
            f"on {target.host}:{target.port} "
            f"(device {target.device_id})"
        )
        return

    console.print(
        f"[red]Write failed[/red]: "
        f"{result.error_kind}: {result.error}"
    )

    raise typer.Exit(code=3)

def _build_target(
    host: str,
    port: int,
    device_id: int,
    timeout: float,
) -> TcpTarget:
    """create and validate a Modbus TCP target."""

    try:
        return TcpTarget(
            host=host,
            port=port,
            device_id=device_id,
            timeout=timeout,
        )

    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc

def _build_scan_plan(
    area: RegisterArea,
    start: int,
    count: int,
    block_size: int,
) -> ScanPlan:
    """create and validate a scan plan."""

    try:
        return ScanPlan(
            start=start,
            count=count,
            block_size=block_size,
            area=area,
        )

    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


def _parse_coil_value(value: int) -> bool:
    """Convert CLI coil value 0/1 into bool."""

    if value == 0:
        return False

    if value == 1:
        return True

    raise typer.BadParameter(
        "coil value must be 0 or 1"
    )

def _parse_coil_values(
    values: str,
) -> tuple[bool, ...]:
    """Parse comma-separated CLI coil values."""

    parts = [
        value.strip()
        for value in values.split(",")
    ]

    if not parts or any(not value for value in parts):
        raise typer.BadParameter(
            "coil values cannot be empty"
        )

    parsed: list[bool] = []

    for value in parts:
        if value == "0":
            parsed.append(False)

        elif value == "1":
            parsed.append(True)

        else:
            raise typer.BadParameter(
                f"invalid coil value {value!r}; "
                "expected only 0 or 1"
            )

    return tuple(parsed)

def _parse_register_values(
    values: str,
) -> tuple[int, ...]:
    """Parse comma-separated CLI register values."""

    parts = [
        value.strip()
        for value in values.split(",")
    ]

    if not parts or any(not value for value in parts):
        raise typer.BadParameter(
            "register values cannot be empty"
        )

    parsed: list[int] = []

    for value in parts:
        try:
            number = int(value)

        except ValueError as exc:
            raise typer.BadParameter(
                f"invalid register value {value!r}"
            ) from exc

        if not 0 <= number <= 65_535:
            raise typer.BadParameter(
                f"register value {number} must be "
                "between 0 and 65535"
            )

        parsed.append(number)

    return tuple(parsed)


# SCAN EXECUTION

def _run_scan(
    host: str,
    port: int,
    device_id: int,
    timeout: float,
    start: int,
    count: int,
    block_size: int,
    area: RegisterArea,
    data_type: DataType | None = None,
    word_order: WordOrder = WordOrder.BIG,
) -> None:
    """execute a Modbus data-area scan."""

    if data_type is not None:
        width = registers_per_value(data_type)

        if count % width != 0:
            raise typer.BadParameter(
                f"--count must be a multiple of {width} "
                f"for --type {data_type.value}"
            )

    target = _build_target(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
    )

    plan = _build_scan_plan(
        area=area,
        start=start,
        count=count,
        block_size=block_size,
    )

    transport = PymodbusTcpTransport(target)
    scanner = Scanner(transport, target)

    try:
        transport.connect()
        report = scanner.scan(plan)

    except ModScannerConnectionError as exc:
        console.print(
            f"[red]Connection failed:[/red] {exc}"
        )
        raise typer.Exit(code=2) from exc

    finally:
        transport.close()

    # render_report(report, console)
    if data_type is None:
        render_report(report, console)
    else:
        render_typed_report(
            report,
            data_type=data_type,
            word_order=word_order,
            console=console,
        )


# WRITE EXECUTION

def _write_single_coil(
    target: TcpTarget,
    address: int,
    value: bool,
) -> None:
    """write one Modbus coil."""

    transport = PymodbusTcpTransport(target)
    writer = Writer(transport, target)

    try:
        transport.connect()

        result = writer.write_coil(
            address=address,
            value=value,
        )

    except ModScannerConnectionError as exc:
        console.print(
            f"[red]Connection failed:[/red] {exc}"
        )
        raise typer.Exit(code=2) from exc

    finally:
        transport.close()

    _render_write_result(result, target)

def _write_multiple_coils(
    target: TcpTarget,
    address: int,
    values: tuple[bool, ...],
) -> None:
    """write multiple Modbus coils."""

    transport = PymodbusTcpTransport(target)
    writer = Writer(transport, target)

    try:
        transport.connect()

        result = writer.write_coils(
            address=address,
            values=values,
        )

    except ModScannerConnectionError as exc:
        console.print(
            f"[red]Connection failed:[/red] {exc}"
        )
        raise typer.Exit(code=2) from exc

    finally:
        transport.close()

    _render_write_result(result, target)

def _write_single_register(
    target: TcpTarget,
    address: int,
    value: int,
) -> None:
    """write one Modbus holding register."""

    transport = PymodbusTcpTransport(target)
    writer = Writer(transport, target)

    try:
        transport.connect()

        result = writer.write_register(
            address=address,
            value=value,
        )

    except ModScannerConnectionError as exc:
        console.print(
            f"[red]Connection failed:[/red] {exc}"
        )
        raise typer.Exit(code=2) from exc

    finally:
        transport.close()

    _render_write_result(result, target)

def _write_multiple_registers(
    target: TcpTarget,
    address: int,
    values: tuple[int, ...],
) -> None:
    """write multiple Modbus holding registers."""

    transport = PymodbusTcpTransport(target)
    writer = Writer(transport, target)

    try:
        transport.connect()

        result = writer.write_registers(
            address=address,
            values=values,
        )

    except ModScannerConnectionError as exc:
        console.print(
            f"[red]Connection failed:[/red] {exc}"
        )
        raise typer.Exit(code=2) from exc

    finally:
        transport.close()

    _render_write_result(result, target)


# SCAN COMMANDS

@scan_app.command("coils")
def scan_coils(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
    ),
) -> None:
    """Scan Modbus coils using FC01."""

    _run_scan(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
        start=start,
        count=count,
        block_size=block_size,
        area=RegisterArea.COIL,
    )

@scan_app.command("discrete-inputs")
def scan_discrete_inputs(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
    ),
) -> None:
    """scan Modbus discrete inputs using FC02."""

    _run_scan(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
        start=start,
        count=count,
        block_size=block_size,
        area=RegisterArea.DISCRETE_INPUT,
    )

@scan_app.command("holding")
def scan_holding_registers(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
    ),
    data_type: DataType | None = typer.Option(
    None,
    "--type",
    help=(
        "Interpret register values as "
        "uint16, int16, uint32, int32, or float32."
    ),  
    ),
    word_order: WordOrder = typer.Option(
        WordOrder.BIG,
        "--word-order",
        help="Word order for multi-register values.",
    ),
) -> None:
    """scan Modbus holding registers using FC03."""

    _run_scan(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
        start=start,
        count=count,
        block_size=block_size,
        area=RegisterArea.HOLDING_REGISTER,
        data_type=data_type,
        word_order=word_order
    )

@scan_app.command("input")
def scan_input_registers(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
    ),
    data_type: DataType | None = typer.Option(
    None,
    "--type",
    help=(
        "Interpret register values as "
        "uint16, int16, uint32, int32, or float32."
    ),
    ),
    word_order: WordOrder = typer.Option(
        WordOrder.BIG,
        "--word-order",
        help="Word order for multi-register values.",
    ),
) -> None:
    """scan Modbus input registers using FC04."""

    _run_scan(
    host=host,
    port=port,
    device_id=device_id,
    timeout=timeout,
    start=start,
    count=count,
    block_size=block_size,
    area=RegisterArea.INPUT_REGISTER,
    data_type=data_type,
    word_order=word_order,
    )


# WRITE COMMANDS

@write_app.command("coil")
def write_coil(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    address: int = typer.Option(
        ...,
        "--address",
        "-a",
        min=0,
        max=65_535,
    ),
    value: int = typer.Option(
        ...,
        "--value",
        "-v",
        help="Coil value: 1=ON, 0=OFF.",
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
) -> None:
    """Write one Modbus coil using FC05."""

    target = _build_target(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
    )

    coil_value = _parse_coil_value(value)

    _write_single_coil(
        target=target,
        address=address,
        value=coil_value,
    )

@write_app.command("coils")
def write_coils(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    address: int = typer.Option(
        ...,
        "--address",
        "-a",
        min=0,
        max=65_535,
    ),
    values: str = typer.Option(
        ...,
        "--values",
        "-v",
        help="Comma-separated coil values, e.g. 1,0,1,0.",
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
) -> None:
    """write multiple Modbus coils using FC15."""

    target = _build_target(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
    )

    parsed_values = _parse_coil_values(values)

    _write_multiple_coils(
        target=target,
        address=address,
        values=parsed_values,
    )

@write_app.command("register")
def write_register(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    address: int = typer.Option(
        ...,
        "--address",
        "-a",
        min=0,
        max=65_535,
    ),
    value: int = typer.Option(
        ...,
        "--value",
        "-v",
        min=0,
        max=65_535,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
) -> None:
    """write one holding register using FC06."""

    target = _build_target(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
    )

    _write_single_register(
        target=target,
        address=address,
        value=value,
    )

@write_app.command("registers")
def write_registers(
    host: str = typer.Option(
        ...,
        "--host",
        "-H",
        help="Modbus TCP hostname or IP address.",
    ),
    address: int = typer.Option(
        ...,
        "--address",
        "-a",
        min=0,
        max=65_535,
    ),
    values: str = typer.Option(
        ...,
        "--values",
        "-v",
        help="Comma-separated register values.",
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
) -> None:
    """write multiple holding registers using FC16."""

    target = _build_target(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
    )

    parsed_values = _parse_register_values(values)

    _write_multiple_registers(
        target=target,
        address=address,
        values=parsed_values,
    )


# NETWORK DISCOVERY

def list_network_interfaces() -> None:
    """Display local network interfaces."""

    addresses = psutil.net_if_addrs()

    table = Table(
        title="Network Interfaces"
    )

    table.add_column("Interface")
    table.add_column("Address")

    for interface_name, interface_addresses in addresses.items():
        for address in interface_addresses:
            table.add_row(
                interface_name,
                str(address.address),
            )

    console.print(table)

def check_modbus_device(
    ip: str,
    device_id: int,
    port: int,
) -> str | None:
    """check whether a host responds as a Modbus TCP device."""

    target = TcpTarget(
        host=ip,
        port=port,
        device_id=device_id,
        timeout=NETWORK_SCAN_TIMEOUT,
    )

    transport = PymodbusTcpTransport(target)

    try:
        transport.connect()

        information = transport.read_device_information(
            device_id
        )

        return information or "Active Modbus Device"

    except ModScannerConnectionError:
        return None

    finally:
        transport.close()

@app.command("scan-network")
def scan_network(
    subnet: str = typer.Option(
        ...,
        "--subnet",
        help="Network to scan, e.g. 100.1.1.0/24.",
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    show_vendor: bool = typer.Option(
        False,
        "--show-vendor",
        help="Attempt to show MAC vendor information.",
    ),
) -> None:
    """discover Modbus TCP devices on a network."""

    if show_vendor and os.geteuid() != 0:
        console.print(
            "Relaunching with sudo for MAC vendor discovery."
        )

        os.execvp(
            "sudo",
            ["sudo", *sys.argv],
        )

    try:
        network = ipaddress.ip_network(
            subnet,
            strict=False,
        )

    except ValueError as exc:
        raise typer.BadParameter(
            f"invalid subnet: {exc}"
        ) from exc

    list_network_interfaces()

    table = Table(
        # title=f"Modbus devices on {network}"
        title = f"Modbus Devices Found on {network}"
    )

    table.add_column("Address")
    table.add_column("Device Info")
    table.add_column("Device ID")
    table.add_column("Vendor")

    console.print(
        f"Scanning {network} on TCP port {port}..."
    )

    found = 0

    hosts = (
        network.hosts()
        if network.prefixlen < 31
        else iter(network)
    )

    for ip in hosts:
        
        ip_string = str(ip)

        information = check_modbus_device(
            ip=ip_string,
            device_id=device_id,
            port=port,
        )

        if information is None:
                console.print(table)
                console.print(
                    f"Found {found} Modbus device(s)."
                )
                continue

        vendor = ""

        if show_vendor:
            try:
                scan_result = nm.scan(
                    ip_string,
                    arguments="-sn",
                )

                raw_host_data: Any = (
                    scan_result
                    .get("scan", {})
                    .get(ip_string, {})
                )

                host_data = cast(
                    dict[str, Any],
                    raw_host_data,
                )

                vendors = cast(
                    dict[str, str],
                    host_data.get("vendor", {}),
                )

                if vendors:
                    vendor = next(
                        iter(vendors.values())
                    )

            except (
                PortScannerError,
                PortScannerTimeout,
            ):
                vendor = "Unknown"
                
        try:
            hostname = socket.gethostbyaddr(
                ip_string
            )[0]

            if information == "Active Modbus Device":
                information = hostname
                # live.update(table)

        except socket.herror:
            pass

        table.add_row(
            ip_string,
            information,
            str(device_id),
            vendor,
        )

        found += 1

        console.print(table)
        console.print(
            f"Found {found} Modbus device(s)."
        )


# LEGACY COMPATIBILITY

@app.command("scan-tcp")
def scan_tcp(
    host: str = typer.Argument(
        ...,
        help="Modbus TCP hostname or IP address.",
    ),
    start: int = typer.Option(
        0,
        "--start",
        "-s",
        min=0,
        max=65_535,
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-c",
        min=1,
        max=65_536,
    ),
    device_id: int = typer.Option(
        1,
        "--device-id",
        "-d",
        min=0,
        max=247,
    ),
    port: int = typer.Option(
        DEFAULT_PORT,
        "--port",
        "-p",
        min=1,
        max=65_535,
    ),
    timeout: float = typer.Option(
        DEFAULT_TIMEOUT,
        "--timeout",
        min=0.1,
    ),
    block_size: int = typer.Option(
        125,
        "--block-size",
        min=1,
        max=125,
    ),
) -> None:
    """scan holding registers using the legacy command."""

    _run_scan(
        host=host,
        port=port,
        device_id=device_id,
        timeout=timeout,
        start=start,
        count=count,
        block_size=block_size,
        area=RegisterArea.HOLDING_REGISTER,
    )

@app.command()
def version() -> None:
    """display the installed ModScanner version."""

    from modscanner import __version__

    console.print(
        f"modscanner {__version__}"
    )


if __name__ == "__main__":
    app()