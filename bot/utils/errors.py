__all__ = ("ClutterError", "ConfigError")


class ClutterError(Exception):
    pass


class ConfigError(ClutterError):
    pass
