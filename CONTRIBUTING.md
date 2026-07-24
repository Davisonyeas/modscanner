# Contributing to ModScanner

First of, thank you for considering a contributing to ModScanner.

ModScanner is intended to become a reliable, safety-first toolkit for Modbus discovery, inspection, decoding, monitoring and controlled validation. The project currently prioritizes a small, correct, tested read-only core over a large unfinished feature set.

## Before contributing

For substantial changes, open an issue before writing code. Describe:

- the problem being solved
- the intended users
- the proposed behavior, 
- safety implications, 
- expected CLI or Python API changes,
- how the change will be tested

Small documentation corrections and focused bug fixes may be submitted directly as pull requests.

## Development setup

Fork the repository, then clone your fork:

```bash 
git clone https://github.com/your_username/modscanner.git
```
```bash
cd modscanner
```

Create a feature branch:
```bash
git switch -c feat/short-description
```

Install all dependency groups:
```bash
uv sync --all-groups
```

Verify the installed project:
```bash
uv run modscanner --help
```
or 

```bash
uv run modscanner version
```

## Project structure

`src/modscanner/`

```text
├── __init__.py
├── cli.py
├── exceptions.py
├── models.py
├── scanner.py
└── reporters/
    ├── console.py
    └── transports/
        ├── base.py
        └── pymodbus_transport.py
```

Keep the protocol-independent scanning behavior out of the CLI and concrete transport modules

- cli.py parses user input and displays the results
- scanner.py contains scanning behavior
- models.py defines stable data structures and enums
- transports/base.py defines transport interfaces
- transports/pymodbus_transport.py adapts PyModbus to the core interfaces
- reporters/ formats completed reports

## Coding standards

- Support the Python versions declared in pyproject.toml
- Add type annotations to public and internal functions
- Use dataclasses or focused model types instead of unstructuted dictionaries when data has a defined shape
- Use project exceptions instead of leaking low-level tranport exceptions
- Keep functions small enough to test directly
- Avoid hidden networ access during import
- Do not add runtime dependencies without explaing why the standard library or existing dependencies are insufficient

Format code:
```bash
uv run ruff format .
```

Run linting:
```bash
uv run ruff check .
```

Run type checking:
```bash
uv run mypy src/modscanner
```

## Testing

### Unit tests

Use fake transports for scanner behavior, including:
- valid blocks
- sparse register maps
- protocol exceptions
- transport failures
- malformed responses
- boundary addresses
- invalid scan plans

Run:
```bash
uv run pytest tests/unit -v
```

### Integration tests

Use a local simulator for end-to-end transport tests. Integration tests must not contact public hosts or require physical equipment.

Run:
```bash
uv run pytest tests/integration -v
```

### Hardware tests

Hardware tests are optional and must be isolated unders tests/hardware/. They must not run as part of the normal test suite.

A hardware test contribution must state:
- manufacturer and model
- firmware version when known
- transport and connection parameters
- function codes exercised
- whether the operation was read-only
- expected and observed behavior

> **Note: Never commit credentials, private IP inventories, customer information, or proprietary configuration data**

## Full verification

Before opening a pull request, do the following:

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
uv run mypy src/modscanner
uv build --no-sources
uv run twine check --strict dist/*
```

## License

By contributing, you agree that your contribution will be licensed under the projects MIT License