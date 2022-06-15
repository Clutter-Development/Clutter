from os import environ
from uvloop import install
from .core import ClutterBot

install()

for key in ["HIDE", "NO_UNDERSCORE"]:
    environ[f"JISHAKU_{key}"] = "True"

ClutterBot.run()  # sure is a funny way to use the classmethod
