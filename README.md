# ModScanner

A safety-first Modbus scanning toolkit for Python.

ModScanner helps engineers inspect Modbus devices without immediately falling back to slow, one-register-at-a-time scanning. It reads registers in blocks and adaptively splits rejected blocks to identify valid and invalid addresses.

> **Project status:** 
Early development. Version 0.1.0 supports only 
> **Modbus TCP holding register scanning. 

## Features 

- Read-only Modbus TCP scanning
- Holding register reads using function code 03
- Configurable device ID, port, timeout, range, and block size
- Adaptive block splitting when a device rejects a register range
- Seperation of protocol errors, transport errors, and invalid responses
- Terminal output using Rich
- Typed Python data module
- Transport abstraction that is built untop of PyModbus
- Unit tested scanning behavior
- Scan all devices on your network that uses Modbus
- Show the slave ID of the Modbus devices

## Installation

Install ModScanner from PyPI using either of two(2) methods the below:

1. Using pip:

```bash
pip install modscanner
```

2. Using uv:

```bash
uv add modscanner
```

Verify the installation using:
```bash
modscanner --help
or
modscanner --h
or 
modscanner version
```

> **The above help shows the commands available, while the version shows the current version you have installd on your machine**

## Quick start

There are different ways to use the library;

### 1. Scan holding registers

1. Quick Scan of 10 registers:

```bash
modscanner scan-tcp 192.168.1.10 --port 502
```

Result:
![ModScanner network discovery example](docs/images/modscanner_tcp_hr_scan_result.png)

2. Scan holding registers `0` through `19` on a Modbus TCP device using the below:

```bash
modscanner scan-tcp 192.168.1.10 --device-id 1 --start 0 --count 20
```

> **The above expects you to use the IP Address of the Modbus device, so replace the 192.168.1.10 with your Modbus device**

3. Specify the TCP port, timeout, and request block size using:

```bash
modscanner scan-tcp 192.168.1.10 --port 502 --device-id 1 --start 0 --count 100 --block-size 50 --timeout 2
```

Run:
```bash
modscanner scan-tcp --help
```

to see all available options.

### 2. Show all devices on your network using Modbus including the slave ID

1. Scan all the devices on your network, and display the devices that are running Modbus:

```bash
modscanner scan-network --subnet 192.168.2.0/24
```

The above shows the list of all devices running Modbus. 

> **Note: You can also get the vendor names, so that you can know what Modbus device has what IP Address. To get the vendor names, root privledge is required, run the below code;

```bash
modscanner scan-network --subnet 192.168.2.0/24 --show-vendor
```

> ***After running the above for the first time, you will be prompted to enter your admin password.

Run:
```bash
modscanner scan-network --help
```

to see all available options.

## Addressing

ModScanner uses zero-based Modbus protocol addresses.

For example, a vendor document may label the first holding register as `40001`, while its protocol address is commonly `0`.

Always confirm how the device manufacturer represents register addresses before scanning.

## Adaptive scanning

Some Modbus devices reject an entire request when only one address is within the requested block is invalid.

ModScanner handles this by:
1. Reading a block of registers.
2. Accepting the block when the response is valid.
3. Splitting a block when the device return a protocol-level error.
4. Continuing until individual valid and invalid addresses are identified.
5. Avoiding recursive requests after transport failure such as timeouts.

This reduces unnecessary requests while stil supporting sparse register maps.

## Safety

ModScanner 0.1.0 is read-only.

It does not write coils or registers. Future write-validation functionality will require explicit register allowlists, value limits, confirmation, readback, and audit logging.

Read-only registers should also be used carefully on production systems. Confirm the target IP address, port, device ID, and permitted register range before scanning industrial equipments.

## Current limitation

Version 0.1.0 does not yet support:

- Modbus RTU
- Coils
- Discrete inputs
- Input registers
- Automatic device ID discovery
- JSON, CSV, or YAML exports
- Data type decoding
- Byte-order or word-order conversion
- Device profiles
- Register monitoring
- Register writes
- Writable-register validation

> **All the above are planned for future releasesa**

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Package PyPI
Visit [https://pypi.org/project/modscanner/](https://pypi.org/project/modscanner/)

## Security

Do not use ModScanner to perform unauthorized scanning or testing.

## Author
Developed by [Davis Onyeoguzoro](https://github.com/davisonyeas)