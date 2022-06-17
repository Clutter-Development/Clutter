"""from __future__ import annotations

import time
from typing import TYPE_CHECKING

from discord import app_commands as app
from discord.ext import commands

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext
    from core.interaction import ClutterInteractionContext


class Miscellaneous(
    commands.Cog,
    name="MODULES.MISCELLANEOUS.NAME",
    description="MODULES.MISCELLANEOUS.DESCRIPTION",
):
    def __init__(self, bot: Clutter, /) -> None:
        self.bot = bot

    @commands.command(
        aliases=["latency", "pong"],
        brief="COMMANDS.PING.BRIEF",
        help="COMMANDS.PING.HELP",
    )
    @commands.bot_has_permissions(
        send_messages=True, read_message_history=True
    )
    async def ping(self, ctx: ClutterContext, /) -> None:
        ping = time.time()

        message = await ctx.reply("** **")

        ping = time.time() - ping

        await message.edit(
            embed=self.bot.embed.info(
                await ctx.i18n("COMMANDS.PING.RESPONSE.TITLE"),
                (await ctx.i18n("COMMANDS.PING.RESPONSE.BODY")).format(
                    ws=int(self.bot.latency * 1000),
                    msg=int(ping * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )

    @app.command(name="ping", description="COMMANDS.PING.BRIEF")  
    async def app_ping(self, ctx: ClutterInteractionContext, /) -> None:
        ping = time.time()

        await ctx.response.send_message("** **")

        ping = time.time() - ping
        await ctx.edit_original_message(
            embed=self.bot.embed.info(
                await ctx.i18n("COMMANDS.PING.RESPONSE.TITLE"),
                (await ctx.i18n("COMMANDS.PING.RESPONSE.BODY")).format(
                    ws=int(self.bot.latency * 1000),
                    msg=int(ping * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )


async def setup(bot: Clutter, /) -> None:
    await bot.add_cog(Miscellaneous(bot))
"""