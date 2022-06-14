__all__ = ("DiscordI18NError", "UnknownTranslationCode", "NoFallback")


class DiscordI18NError(Exception):
    """The base exception class for this library."""


class UnknownTranslationCode(DiscordI18NError):
    """Raised when a translation string doesn't exist."""

    def __init__(self, code: str, /) -> None:
        self.code = code

    def __str__(self) -> str:
        return f"Unknown translation code: {self.code}"


class NoFallback(DiscordI18NError):
    """Raised when the fallback language isn't in the provided languages."""

    def __init__(
        self, fallback_language: str, language_file_directory, /
    ) -> None:
        self.fallback_language = fallback_language
        self.language_file_directory = language_file_directory

    def __str__(self) -> str:
        return f"The fallback language ({self.fallback_language}) does not exist in the languages directory ({self.language_file_directory})."
