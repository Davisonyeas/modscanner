"""Example: write one Modbus coil using FC05."""

from modscanner.writer import Writer
from modscanner.models import TcpTarget
from modscanner.transports.pymodbus_transport import PymodbusTcpTransport

def main() -> None:
    target = TcpTarget(
        host="127.0.0.1",
        device_id=1,
    )

    transport = PymodbusTcpTransport(target)
    writer = Writer(transport, target)

    transport.connect()

    try:
        result = writer.write_coil(
            address=0,
            value=True,
        )

        if result.ok:
            print("Coil written successfully.")
        else:
            print(f"Write failed: {result.error}")

    finally:
        transport.close()


if __name__ == "__main__":
    main()