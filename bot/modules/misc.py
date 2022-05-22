from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from discord import app_commands as app

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext

CommandMapping = dict[commands.Cog, list[commands.Command | commands.Group]]


class Dropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption], values: dict[str, discord.Embed], /, *, placeholder: str = None) -> None:
        self.options = options
        self.values_ = values

        super().__init__(options=options.keys(), placeholder=placeholder, min_values=1, max_values=1)  # type: ignore

    async def callback(self, interaction: discord.Interaction):
        await interaction.edit_original_message(embed=self.values_[self.values[0]])


class DropdownView(discord.ui.View):
    def __init__(self, options: list[discord.SelectOption], values: dict[str, discord.Embed], /, *, placeholder: str = None) -> None:
        super().__init__()
        self.add_item(Dropdown(options, values, placeholder=placeholder))
    

class ClutterHelpCommand(commands.HelpCommand):
    cog: Misc

    async def send_bot_help(self, mapping: CommandMapping, /):
        dropdown_options = []
        dropdown_values = {}

        dropdown_options.append(discord.SelectOption(emoji="📄", label="Index", value="General info about the bot"))
        h_embed = self.cog.bot.embed.info("Showing general gelp for the bot", "Clutter is a Discord bot that is designed to be a simple and easy to use.")
        h_embed.add_field(name="Markdown Reference", value="`<parameter>` - This means the parameter is **required**")

        for cog, commands_list in mapping.items():
            if cog.qualified_name == "Jishaku":
                continue

            emoji, label = cog.qualified_name.split(" ", 1)
            cog_embed = self.cog.bot.embed.info(f"Showing help for the module: {label}", cog.description)
            for command in commands_list:
                if command.hidden:
                    continue
                cog_embed.add_field(name=self.get_command_signature(command), value=command.brief)

            dropdown_options.append(discord.SelectOption(emoji=emoji, label=label, description=cog.description))
            dropdown_values[label] = cog_embed
        await self.context.reply(view=DropdownView(dropdown_options, dropdown_values, placeholder="Select a module to view help for..."))


class Misc(commands.Cog, name="🔧 Miscellanious", description="Miscellanious commands"):
    def __init__(self, bot: Clutter):
        self.bot = bot

        # help command is basically in this cog
        self._original_help_command = bot.help_command
        bot.help_command = ClutterHelpCommand()
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command
