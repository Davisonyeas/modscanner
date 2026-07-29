"""command-line interface for ModScanner"""

import os
import sys
import nmap
import typer
import psutil
import socket
import ipaddress

from rich.console import Console
from modscanner.exceptions import ModScannerConnectionError, ModbusException
from modscanner.models import ScanPlan, TcpTarget
from modscanner.reporters.console import render_report
from modscanner.scanner import Scanner
from modscanner.transports.pymodbus_transport import (
    PymodbusTcpTransport,
)

from nmap import PortScannerError, PortScannerTimeout

from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="modscanner",
    help="safely discover and inspect Modbus devices via RTU and TCP.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["--help", "--h", "-help", "--h"]},
)

PORT = 502
TIMEOUT = 0.5
COMMON_SLAVE_IDS = [1, ]

FOUND_MODBUS_DEVICES = 0
ALL_IPS_FOUND = []

console = Console()

nm = nmap.PortScanner()

def list_network_interfaces():
    addresses = psutil.net_if_addrs()
    output = console or Console()

    table = Table(
        title=(
            f"List of Network Interfaces: "
        )
    )
    table.add_column("Network Interface")
    table.add_column("Address")

    print("Which of the network interfaces do you want to scan: ")
    for interface_name, interface_addr in addresses.items():
        for address in interface_addr:
            table.add_row(str(interface_name), str(address.address))

    output.print(table)

def check_modbus_devices(ip, slave_id):
    """checking Modbus devices on the network"""

    global FOUND_MODBUS_DEVICES, ALL_IPS_FOUND

    target = TcpTarget(
                host=ip, 
                port=PORT,
                timeout=TIMEOUT, 
            )

    transport = PymodbusTcpTransport(target)
    
    try:
        connected = transport.connect()
        print(f"[FOUND] \n IP Address: {ip} \n SLAVE  {slave_id}")
        FOUND_MODBUS_DEVICES = FOUND_MODBUS_DEVICES + 1
        ALL_IPS_FOUND.append(ip)
        print(f"MODBUS DEVICES SO FAR \n")
        for idx, dev in enumerate(ALL_IPS_FOUND):
            print(f"{idx+1}: {ip}")
            

    except (ModbusException, ModScannerConnectionError) as exc:
        # Instead of crashing, print a message and return None
        console.print(f"[OFFLINE] {ip}:{PORT} - {exc}")
        return None

    if not connected:
        print("NO Modbus device")
        return None

    FOUND_MODBUS_DEVICES = FOUND_MODBUS_DEVICES + 1
    response = transport.read_device_information(slave_id)
    print(f"rseponse = {response}")


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


@app.command("scan-network")
def scan_network(
    subnet: str = typer.Option(
        ..., 
        "--subnet",
        help="subnet or IP range of your network Modbus interface. \n\n Example: modscanner scan-network --subnet 192.168.2.0/24",
    ),
    show_vendor: bool = typer.Option(
        False,
        "--show-vendor",
        help="Enable root (sudo) privledge do discover MAC hardware vendor names.\n" \
        "This allows you to see what ip belongs to what device/vendor name."
    )
) -> None:
    """scan all the Modbus devices on the network"""

    # checking root priv
    if show_vendor is True:
        if os.geteuid() != 0:
            print("Relaunching with sudo to capture MAC address vendor name")

            try:
                os.execvp("sudo", ["sudo"] + sys.argv)

            except Exception as e:
                print(f"Failed to elevate privledges: {e}")
                sys.exit(1)

    output = console or Console()

    table = Table(
        title=(
            f"Modbus devices on netwrk: "
        )
    )
    table.add_column("Address")
    table.add_column("Device Info")
    table.add_column("Slave ID")

    list_nrk_interfaces = list_network_interfaces()
    
    print(f"Starting Modbus scan on {subnet}....")
    network = ipaddress.ip_network(subnet, strict=False)

    # skip netwrk and bradcast addresses fr standard subnets
    hosts = list(network.hosts() if network.prefixlen < 31 else list(network))

    for ip in hosts:

        ip_str = str(ip)

        for slave_id in COMMON_SLAVE_IDS:
            # device_info = check_modbus_devices_on_network(ip, slave_id)
            device_info = check_modbus_devices(str(ip), slave_id)
            print(f"device info = {device_info}")
            print(f"[TOTAL MODBUS DEVICES: {FOUND_MODBUS_DEVICES}]")

        print(f"ALLL IPs = {set(ALL_IPS_FOUND)}")
        if str(ip) in ALL_IPS_FOUND:
            for ip in ALL_IPS_FOUND:
                nm_scan = nm.scan(ip_str, arguments="-sn")
                
                vendor_name = "Unknown Vendor"
        
                if ip_str in nm_scan["scan"]:
                    host_data = nm_scan["scan"][ip_str]
        
                    if "vendor" in host_data and host_data["vendor"]:
                        vendor_name = list(host_data["vendor"].values())[0]
                        # requires sudo to extract vendor name, ignnore
                        print("vendor name", vendor_name)

                    else:
                        print("#" * 50)
                        print("Use the example command below to get vendor name, passwrd required: \n")
                        print("modscanner scan-network --subnet 172.16.2.0/24 --show-vendor")
                        print("#" * 50)

                try:
                    h_name = socket.gethostbyaddr(ip)[0]

                except socket.herror:
                    print(f"Could not resolve IP adddress")

            table.add_row(
                ip,
                vendor_name,
                str(slave_id)
            )

        output.print(table)

@app.command()
def version() -> None:
    """display the installed ModScanner version"""

    from modscanner import __version__

    console.print(f"modscanner {__version__}")

if __name__ == "__main__":
    app()
