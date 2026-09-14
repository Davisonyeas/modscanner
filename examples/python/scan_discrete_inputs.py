"""Example: scan Modbus discrete inputs using FC02."""

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
        count=8,
    )

    transport = PymodbusTcpTransport(target)
    scanner = Scanner(transport, target)

    transport.connect()

    try:
        report = scanner.scan_discrete_inputs(plan)

        for result in report.results:
            print(
                f"Discrete input {result.address}: "
                f"{result.value if result.value is not None else result.error}"
            )

    finally:
        transport.close()


if __name__ == "__main__":
    main()