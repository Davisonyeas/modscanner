# modscanner Examples

ModScanner can be used in two ways:

## Command Line

See [`cli/`](cli/) for examples using the `modscanner` command.

The shell scripts in `/cli` can be executed directly.

If you created the files manually and they are not executable, run:

```bash
chmod +x examples/cli/*.sh
```

THen
```bash
./examples/cli/scan_registers.sh
```

## Python API

See [`python/`](python/) for examples integrating modscanner directly into
Python applications.

---
# Examples

## CLI
---

## `examples/cli/README.md`

# ModScanner CLI Examples

These scripts demonstrate common ModScanner CLI operations.

Replace the IP addresses, device IDs, addresses, and values with values
appropriate for your Modbus device.

## Read Operations

| Script | Function |
|---|---|
| `scan_network.sh` | Discover Modbus TCP devices |
| `scan_coils.sh` | Read coils using FC01 |
| `scan_discrete_inputs.sh` | Read discrete inputs using FC02 |
| `scan_holding_registers.sh` | Read holding registers using FC03 |
| `scan_input_registers.sh` | Read input registers using FC04 |

## Write Operations

| Script | Function |
|---|---|
| `write_coil.sh` | Write one coil using FC05 |
| `write_register.sh` | Write one holding register using FC06 |
| `write_coils.sh` | Write multiple coils using FC15 |
| `write_registers.sh` | Write multiple holding registers using FC16 |

## Default Port

Port `502` is used by default.

To use another port:

```bash
modscanner scan holding \
    --host 127.0.0.1 \
    --port 1502 \
    --device-id 1 \
    --start 0 \
    --count 10
```