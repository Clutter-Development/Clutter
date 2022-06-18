from __future__ import annotations

__all__ = ("I18NError", "UnknownTranslationCode", "NoFallback")


class I18NError(Exception):
    pass


class UnknownTranslationCode(I18NError):
    def __init__(self, code: str, /) -> None:
        self.code = code

    def __str__(self) -> str:
        return f"Unknown translation code: {self.code}"


class NoFallback(I18NError):
    def __init__(
        self, fallback_language: str, language_file_directory: str, /
    ) -> None:
        self.fallback_language = fallback_language
        self.language_file_directory = language_file_directory

    def __str__(self) -> str:
        return f"The fallback language ({self.fallback_language}) does not exist in the languages directory ({self.language_file_directory})."
