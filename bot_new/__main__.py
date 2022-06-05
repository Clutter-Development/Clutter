import sentry_sdk
from core.bot import bot
import uvloop

uvloop.install()

sentry_sdk.init(bot._config["SENTRY_KEY"], traces_sample_rate=1.0)

bot.run()
