# modscanner Python API Examples

This directory contains examples for using modscanner as a Python library.

## Installation

Install ModScanner into your Python environment:

```bash
pip install modscanner
```

For local development:
```bash
uv sync 
source .venv/bin/activate
```

## Modbus TCP Target
Create a target:
```python
from modscanner.models import TcpTarget

target = TcpTarget(
    host="127.0.0.1",
    device_id=1,
)
```

## Transport
Create a PyModbus-backed transport:
```python
from modscanner.transports.pymodbus_transport import PymodbusTcpTransport

transport = PymodbusTcpTransport(target)
```
Connect before performing operations:
```python
transport.connect()
```

Always close the conection when finished:
```python
transport.close()
```

A recommended pattern is:
```python
transport.connect()

try:
    # Modbus operations

finally:
    transport.close()
```

## Reading
Available scan operations:
- scanner.scan_coils(plan)
- scanner.scan_discrete_inputs(plan)
- scanner.scan_holding_registers(plan)
- scanner.scan_input_registers(plan)

See:
- [scan_holding_registers.py](scan_holding_registers.py)

## Writing
Available write operations
- writer.write_coil(*)
- writer.write_coils(*)
- writer.write_register(*)
- writer.write_registers(*)

See:
- [write_coil.py](write_coil.py)
- [write_coils.py](write_coils.py)
- [write_register.py](write_register.py)
- [write_registers.py](write_registers.py)

The Python API uses native Python booleans for coils:
- True
- False

while the CLI uses for convenience:
- 1
- 0

## Safety
Writing Modbus coils or registers can modify the state or configuration of physical equipments like VFDs, inverters, sensors, etc.

Make sure to verify the target device, address, and value before performing write operations.

---
# scan coils
`examples/python/scan_coils.py`

```python
"""Example: scan Modbus coils using FC01."""

from modscanner.models import ScanPlan, TcpTarget
from modscanner.scanner import Scanner
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
        report = scanner.scan_coils(plan)

        for result in report.results:
            print(
                f"Coil {result.address}: "
                f"{result.value if result.value is not None else result.error}"
            )

    finally:
        transport.close()


if __name__ == "__main__":
    main()
```

---

---
# scan holding registers

`examples/python/scan_holding_registers.py`

```python
"""Example: scan Modbus holding registers."""

from modscanner.models import ScanPlan, TcpTarget
from modscanner.scanner import Scanner
from modscanner.transports.pymodbus_transport import PymodbusTcpTransport

def main() -> None:
    """scan holding registers and print the results"""

    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )

    plan = ScanPlan(
        start=0,
        count=20,
        block_size=10,
    )

    transport = PymodbusTcpTransport(target)
    scanner = Scanner(transport, target)

    transport.connect()

    try:
        report = scanner.scan_holding_registers(plan)

        print(
            f"Target: {target.host}:{target.port} "
            f"(device {target.device_id})"
        )

        print(
            f"Successful: {report.successful_count} | "
            f"Failed: {report.failed_count}"
        )

        print()

        for result in report.results:
            if result.value is not None:
                print(
                    f"Address {result.address}: "
                    f"{result.value}"
                )
            else:
                print(
                    f"Address {result.address}: "
                    f"{result.status} "
                    f"({result.error})"
                )

    finally:
        transport.close()


if __name__ == "__main__":
    main()