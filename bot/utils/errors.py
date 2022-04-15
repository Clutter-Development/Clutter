__all__ = ("ClutterError", "ConfigError")


class ClutterError(Exception):
    pass


class ConfigError(ClutterError):
    def __init__(self, error: Exception, /):
        self.error = error

    def __str__(self):
        if isinstance(self.error, KeyError):
            return f"ConfigError: {self.error}: Missing required keys in config.json5."
        elif isinstance(self.error, ValueError):
            return f"ConfigError: {self.error}: config.json5 syntax is broken."
        elif isinstance(self.error, FileNotFoundError):
            return f"ConfigError: {self.error}: config.json5 not found, perhaps you forgot to rename config.example.json5 to config.json5?"
