from __future__ import annotations

from asyncio import run
from contextlib import suppress
from os import environ

from sentry_sdk import init
from uvloop import install

from .core import ClutterBot


async def main() -> None:
    async with await ClutterBot.init() as bot:
        init(bot.config["SENTRY_URL"], traces_sample_rate=1.0)

        install()

        for key in ["HIDE", "NO_UNDERSCORE"]:
            environ[f"JISHAKU_{key}"] = "True"

        await bot.start(bot.token)


with suppress(KeyboardInterrupt):
    run(main())
