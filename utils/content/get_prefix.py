from typing import Callable

from config import defaults


def get_prefix(db) -> Callable:
    def prefix(bot, message):
        return db.get(f"servers.{message.guild.id}.prefix", defaults["prefix"])

    return prefix
