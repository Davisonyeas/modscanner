"""Example: scan Modbus input registers using FC04."""

from modscanner.scanner import Scanner
from modscanner.models import ScanPlan, TcpTarget
from modscanner.transports.pymodbus_transport import PymodbusTcpTransport

def main() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )

    plan = ScanPlan(
        start=0,
        count=10,
    )

    transport = PymodbusTcpTransport(target)
    scanner = Scanner(transport, target)

    transport.connect()

    try:
        report = scanner.scan_input_registers(plan)

        for result in report.results:
            print(
                f"Input register {result.address}: "
                f"{result.value if result.value is not None else result.error}"
            )

    finally:
        transport.close()


if __name__ == "__main__":
    main()