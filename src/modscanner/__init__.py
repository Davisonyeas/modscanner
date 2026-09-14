"""ModScanner public package interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version

from modscanner.models import (
    RegisterArea,
    RegisterResult,
    ResultStatus,
    ScanPlan,
    ScanReport,
    TcpTarget,
)
from modscanner.scanner import Scanner
from modscanner.writer import Writer

try:
    __version__ = version("modscanner")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "RegisterArea",
    "RegisterResult",
    "ResultStatus",
    "ScanPlan",
    "ScanReport",
    "Scanner",
    "TcpTarget",
    "Writer",
    "__version__",
]