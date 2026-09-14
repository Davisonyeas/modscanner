# Safety

Modbus devices may control physical equipment.

Write operations must be used carefully.

Before writing a coil or holding register, verify:

1. Target IP address
2. TCP port
3. Device ID
4. Register or coil address
5. Whether the address is writable
6. Permitted value range
7. Physical effect of the write

Do not experiment with unknown writable addresses on production systems.

## Read Operations

Read operations are safer than writes but can still affect constrained
industrial devices if excessive scanning generates unnecessary traffic.

Use appropriate ranges and timeouts when scanning production systems.

## Authorization

Only scan or modify devices that you are authorized to access.