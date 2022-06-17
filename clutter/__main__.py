from asyncio import run
from os import environ

from sentry_sdk import init
from uvloop import install

from .core import init_bot

install()

for key in ["HIDE", "NO_UNDERSCORE"]:
    environ[f"JISHAKU_{key}"] = "True"


async def runner() -> None:
    async with await init_bot() as bot:
        init(bot.config["SENTRY_URL"], traces_sample_rate=1.0)
        await bot.start(bot.token)


try:
    run(runner())
except KeyboardInterrupt:
    pass
