from __future__ import annotations

import time
from typing import TYPE_CHECKING

import discord.ui
from discord.ext import commands

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext

CommandMapping = dict[commands.Cog, list[commands.Command | commands.Group]]


class ClutterHelpCommand(commands.HelpCommand):
    cog: Misc

    def get_command_signature(self, command: commands.Command, /) -> str:
        parent: commands.Group | None = command.parent  # type: ignore
        entries = []
        while parent:
            entries.append(f"{parent.name} {parent.signature}".strip())
            parent = parent.parent  # type: ignore
        parent_signature = " ".join(reversed(entries))
        return f"{self.context.prefix}{parent_signature} {command.signature}"

    async def send_bot_help(self, mapping: CommandMapping, /):
        pass


class Misc(
    commands.Cog,
    name="MODULES.MISCELLANIOUS.NAME",
    description="MODULES.MISCELLANIOUS.DESCRIPTION",
):
    def __init__(self, bot: Clutter):
        self.bot = bot

        # help command is basically in this cog
        self._original_help_command = bot.help_command
        bot.help_command = ClutterHelpCommand(
            verify_checks=False, brief="COMMANDS.HELP.BRIEF", help="COMMANDS.HELP.HELP"
        )
        bot.help_command.cog = self

    async def cog_unload(self) -> None:
        self.bot.help_command = self._original_help_command

    @commands.command(
        aliases=["latency"], brief="COMMANDS.PING.BRIEF", help="COMMANDS.PING.HELP"
    )
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def ping(self, ctx: ClutterContext):
        ts = time.monotonic()
        message = await ctx.reply("** **", mention_author=False)
        await message.edit(
            embed=self.bot.embed.info(
                await self.bot.i18n(ctx, "COMMANDS.PING.RESPONSE.TITLE"),
                (await self.bot.i18n(ctx, "COMMANDS.PING.RESPONSE.BODY")).format(
                    ws_ping=self.bot.latency * 1000,
                    message_ping=int((time.monotonic() - ts) * 1000),
                    db_ping=0,
                ),
            )
        )  # TODO: database ping

    @commands.command(
        aliases=["support"], brief="COMMANDS.INVITE.BRIEF", help="COMMANDS.INVITE.HELP"
    )
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def invite(self, ctx: ClutterContext):
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=await self.bot.i18n("COMMANDS.INVITE.BUTTONS.BOT_INVITE"),
                url=self.bot.invite_url,
            )
        )
        view.add_item(
            discord.ui.Button(
                label=await self.bot.i18n("COMMANDS.INVITE.BUTTONS.DISCORD_INVITE"),
                url=self.bot.discord_invite,
            )
        )
        await ctx.reply_embed("info", view=view)


async def setup(bot: Clutter):
    await bot.add_cog(Misc(bot))
