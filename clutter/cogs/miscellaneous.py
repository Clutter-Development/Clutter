from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING

from discord.app_commands import command as slash_command
from discord.ext.commands import Cog, bot_has_permissions, command

if TYPE_CHECKING:
    from ..core import ClutterBot, ClutterContext, ClutterInteraction


class Miscellaneous(
    Cog,
    name="MODULES.MISCELLANEOUS.NAME",
    description="MODULES.MISCELLANEOUS.DESCRIPTION",
):
    def __init__(self, bot: ClutterBot) -> None:
        self.bot = bot

    @command(
        aliases=("latency",),
        brief="COMMANDS.PING.BRIEF",
        help="COMMANDS.PING.HELP",
    )
    @bot_has_permissions(
        send_messages=True, read_message_history=True, use_external_emojis=True
    )
    async def ping(self, ctx: ClutterContext) -> None:
        ping = monotonic()

        message = await ctx.reply("** **")

        ping = monotonic() - ping

        await message.edit(
            embed=self.bot.embed.info(
                await ctx.i18n("COMMANDS.PING.RESPONSE.TITLE"),
                await ctx.i18n(
                    "COMMANDS.PING.RESPONSE.BODY",
                    ws=int(self.bot.latency * 1000),
                    msg=int(ping * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )

    @slash_command(name="ping", description="COMMANDS.PING.BRIEF")
    async def slash_ping(self, ctx: ClutterInteraction) -> None:
        ping = monotonic()

        await ctx.response.send_message("** **")

        ping = monotonic() - ping
        await ctx.edit_original_message(
            embed=self.bot.embed.info(
                await ctx.i18n("COMMANDS.PING.RESPONSE.TITLE"),
                await ctx.i18n(
                    "COMMANDS.PING.RESPONSE.BODY",
                    ws=int(self.bot.latency * 1000),
                    msg=int(ping * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )


async def setup(bot: ClutterBot) -> None:
    await bot.add_cog(Miscellaneous(bot))
