from __future__ import annotations

import os

import sentry_sdk
import uvloop
from core.bot import bot

uvloop.install()

sentry_sdk.init(bot.config["SENTRY_KEY"], traces_sample_rate=1.0)

for key in ["HIDE", "NO_UNDERSCORE"]:
    os.environ[f"JISHAKU_{key}"] = "True"

bot.run()
