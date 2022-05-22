from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from discord import app_commands as app

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext

CommandMapping = dict[commands.Cog, list[commands.Command | commands.Group]]


class ClutterHelpCommand(commands.HelpCommand):
    cog: Misc

    async def send_bot_help(self, mapping: CommandMapping, /):
        pass


class Misc(commands.Cog, name="🔧 Miscellanious", description="Miscellanious commands"):
    def __init__(self, bot: Clutter):
        self.bot = bot

        # help command is basically in this cog
        self._original_help_command = bot.help_command
        bot.help_command = ClutterHelpCommand()
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command
