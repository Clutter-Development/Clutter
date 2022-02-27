from typing import Callable

from discord.ext import commands

from config import defaults


def get_prefix(db) -> Callable:
    def prefix(bot, message):
        return commands.when_mentioned_or(*db.get(f"servers.{message.guild.id}.prefix", defaults["prefix"]))(bot,
                                                                                                             message)

    return prefix
