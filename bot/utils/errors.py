__all__ = ("ClutterError", "ConfigError")


class ClutterError(Exception):
    """Base class for all Clutter errors."""
    pass


class ConfigError(ClutterError):
    """Raised when a configuration file is invalid/not found."""
    pass
