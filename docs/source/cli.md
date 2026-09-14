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