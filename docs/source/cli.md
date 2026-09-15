# Command-Line Interface

Display the main help page:

```bash
modscanner --help
```

## Scan Commands
```bash
modscanner scan --help
```

Available scan commands include:
- coils
- discrete inputs
- holding
- input

## Common Scan Options
- --host
- --port
- --device-id
- --start
- --count
- --block-size
- --timeout

### Example
```bash
modscanner scan holding \
    --host 192.168.1.10 \
    --port 502 \
    --device-id 1 \
    --start 0 \
    --count 100 \
    --block-size 50 \
    --timeout 2
```

## Typed Register Decoding

Holding registers (FC03) and input registers (FC04) can be
interpreted as common numeric data types.

Supported types:

- `uint16`
- `int16`
- `uint32`
- `int32`
- `float32`

Raw 16-bit register values remain the default.

### Float32 example

```bash
modscanner scan holding \
    --host 10.1.1.47 \
    --device-id 1 \
    --start 0 \
    --count 2 \
    --type float32
```

For devices that store the low word first:
```bash
modscanner scan holding \
    --host 10.1.1.47 \
    --device-id 1 \
    --start 0 \
    --count 2 \
    --type float32 \
    --word-order little
```

A 32-bit value requires two consecutive 16-bit Modbus
registers. Therefore --count must be a multiple of 2 for
32-bit types.

```python
from modscanner import DataType, WordOrder, decode_registers

value = decode_registers(
    (32768, 17392),
    DataType.FLOAT32,
    WordOrder.LITTLE,
)

print(value)
```


## Write Commands
```bash
modscanner write --help
```

Available commands inlcude:
- coil
- coils
- register
- registers

### Write Multiple Coils
```bash
modscanner write coils \
    --host 192.168.1.10 \
    --address 0 \
    --values 1,0,1,0
```

### Write Multiple Holding Registers
```bash
modscanner write registers \
    --host 192.168.1.10 \
    --address 100 \
    --values 10,20,30,40
```

---
## Legacy Command
The original holding-register command remains available:
```bash
modscanner scan-tcp 192.168.1.10 \
    --start 0 \
    --count 20
```