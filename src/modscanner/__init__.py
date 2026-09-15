"""ModScanner public package interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from modscanner.models import (
    DataType,
    RegisterArea,
    RegisterResult,
    ResultStatus,
    ScanPlan,
    ScanReport,
    TcpTarget,
    WordOrder,
)
from modscanner.scanner import Scanner
from modscanner.writer import Writer
from modscanner.decoder import registers_per_value

try:
    __version__ = version("modscanner")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "DataType",
    "RegisterArea",
    "RegisterResult",
    "ResultStatus",
    "ScanPlan",
    "ScanReport",
    "Scanner",
    "TcpTarget",
    "WordOrder",
    "Writer",
    "decode_registers",
    "registers_per_value",
    "__version__",
]