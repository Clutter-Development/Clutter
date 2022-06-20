from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypedDict, overload

from .embed import Embed

if TYPE_CHECKING:
    import datetime

    class StyleDict(TypedDict):
        EMOJIS: dict[str, str]
        COLORS: dict[str, int]

    class PartialEmbed(Protocol):
        def __call__(
            self,
            title: str | None = None,
            description: str | None = None,
            *,
            url: str | None = None,
            timestamp: datetime.datetime | None = None,
        ) -> Embed:
            ...


__all__ = ("EmbedCreator",)


class EmbedCreator:
    def __init__(self, style: StyleDict) -> None:
        self._style = style

    def __getattr__(self, item: str) -> PartialEmbed:
        return self.__call__(item)

    @overload
    def __call__(self, asset_type: str, /) -> PartialEmbed:
        ...

    @overload
    def __call__(
        self,
        asset_type: str,
        /,
        title: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> Embed:
        ...

    def __call__(
        self,
        asset_type: str,
        /,
        title: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> Embed | PartialEmbed:
        # noinspection PyShadowingNames
        def inner(
            title: str | None = title,
            description: str | None = description,
            **kwargs_: Any,
        ) -> Embed:
            nonlocal asset_type
            asset_type = asset_type.upper()

            if not kwargs_:
                kwargs_ = kwargs

            return Embed(
                title=(
                    f"{self._style.get('EMOJIS', {}).get(asset_type, '')} {title}"
                    .strip()
                    if title
                    else None
                ),
                description=description,
                color=self._style.get("COLORS", {}).get(asset_type),
                **kwargs_,
            )

        if not any([title, description, kwargs]):
            return inner

        return inner()
