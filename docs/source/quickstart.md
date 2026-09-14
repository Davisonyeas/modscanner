# Quick Start

## Scan Holding Registers

```bash
modscanner scan holding \
    --host 192.168.1.10 \
    --start 0 \
    --count 20
```

modscanner uses:
- TCP port 502 by default
- device ID 1 by default
- zero-based Modbus protocol addresses

## Read Coils
```bash
modscanner scan coils \
    --host 192.168.1.10 \
    --start 0 \
    --count 8
```

## Read Discrete Inputs
```bash
modscanner scan discrete-inputs \
    --host 192.168.1.10 \
    --start 0 \
    --count 8
```

## Read Input Registers
```bash
modscanner scan input \
    --host 192.168.1.10 \
    --start 0 \
    --count 20
```

## Write a Coil
```bash
modscanner write coil \
    --host 192.168.1.10 \
    --address 0 \
    --value 1
```

CLI coil values are:
- 1 = ON | True
- 0 = OFF | False

## Writing a Holding Register
```bash
modscanner write register \
    --host 192.168.1.10 \
    --address 100 \
    --value 50
```

---
# Network Discovery
```bash
modscanner scan-network \
    --subnet 192.168.1.0/24
```

To attempt vendor discovery
```bash
modscanner scan-network \
    --subnet 192.168.1.0/24 \
    --show-vendor
```

