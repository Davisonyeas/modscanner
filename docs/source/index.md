# ModScanner

modscanner is a Python toolkit for discovering, inspecting, scanning, and interacting with Modbus TCP devices.

It provides both a command-line interface and a Python API.

```{toctree}
:maxdepth: 2
:caption: Documentation

installation
quickstart
cli
safety
api/scanner
api/writer
api/models
api/transports
```

## Supported Modbus Operations

| Function Code | Operation                        |
| ------------- | -------------------------------- |
| FC01          | Read Coils                       |
| FC02          | Read Discrete Inputs             |
| FC03          | Read Holding Registers           |
| FC04          | Read Input Registers             |
| FC05          | Write Single Coil                |
| FC06          | Write Single Holding Register    |
| FC15          | Write Multiple Coils             |
| FC16          | Write Multiple Holding Registers |


## Quick Example
```bash
modscanner scan holding \
    --host 192.168.1.10 \
    --device-id 1 \
    --start 0 \
    --count 20
```

> *[!WARNING] Modbus write operations can affect physical equipment. Always verify the target device, address, function, and value before issuing
write commands.