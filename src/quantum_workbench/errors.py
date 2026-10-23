"""User-facing errors with actionable diagnostics."""


class WorkbenchError(Exception):
    """Base class for expected application errors."""


class UnsupportedOperationError(WorkbenchError, ValueError):
    """The selected simulator cannot model an operation correctly."""


class ResourceLimitError(WorkbenchError, ValueError):
    """An explicit, configurable memory/size guard was exceeded."""
