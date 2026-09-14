# modscanner CLI Examples

This current directory contains examples for using modscanner from the command line.

Modbus TCP port `502` is used by default. Use `--port` to connect to a
different port.

All example IP addresses, device IDs, register addresses, and values are
examples only. Replace them with values appropriate for your Modbus device.

## Scan for Modbus devices

```bash
./scan_network.sh
```

## Scan holding registers


```bash
./scan_registers.sh
```

## Write a single coil

```bash
./scan_registers.sh
```

## Write multiple coils

```bash
./scan_registers.sh
```

## Write a single holdin register

```bash
./scan_registers.sh
```

## Write multiple holding registers

```bash
./scan_registers.sh
```

## Custom Modbus TCP Port
Port 502 is the default Modbus port.

To use a different port:

```bash
modscanner scan-registers \
    --host 127.0.0.1 \
    --port 1502 \
    --device-id 1 \
    --start 0 \
    --count 10
```

## Coil Values
CLI coil values use:
- 1 = ON | True
- 0 = OFF | False

Example:
```bash
modscanner write-coil \
    --host 127.0.0.1 \
    --address 0 \
    --value 1
```
Multiple coils can be written using comma-seperated values:
```bash
modscanner write-coils \
    --host 127.0.0.1 \
    --address 0 \
    --values 1,0,1,0
```

## Safety
Modbus write operations can change the state or configuration of physical equipments like VFDs, inverters, etc.

It is important to verify the target device, address, and value before running a write command.


---

# `examples/cli/scan_network.sh`

```bash
#!/usr/bin/env bash

set -e

# Example: discover Modbus TCP devices on a network.

# Replace the subnet with the network you want to scan.

SUBNET="100.1.1.0/24"

modscanner scan-network \
    --subnet "$SUBNET"
```