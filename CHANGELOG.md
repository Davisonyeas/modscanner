# Changelog

All notable changes to ModScanner will be documented in this file

## [0.1.0] - 2026-07-23

### Added

- Read-only Modbus TCP holding-register scanning
- Adaptive splitting of rejected register blocks
- Protocol, transport, and invalid-response classification
- Configurable host, port, device ID, timeout, range, and block size
- Rich terminal reporting
- Local PyModbus simulator and integration test
- Unit tests for sparse register ranges and transport failures