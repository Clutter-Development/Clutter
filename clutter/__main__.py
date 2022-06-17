from asyncio import run
from contextlib import suppress
from os import environ

from sentry_sdk import init
from uvloop import install

from .core import ClutterBot

install()

for key in ["HIDE", "NO_UNDERSCORE"]:
    environ[f"JISHAKU_{key}"] = "True"


async def runner() -> None:
    async with await ClutterBot.init() as bot:
        init(bot.config["SENTRY_URL"], traces_sample_rate=1.0)
        await bot.start(bot.token)


with suppress(KeyboardInterrupt):
    run(runner())
