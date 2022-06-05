import sentry_sdk
import uvloop
from core.bot import bot

uvloop.install()

sentry_sdk.init(bot._config["SENTRY_KEY"], traces_sample_rate=1.0)

bot.run()
