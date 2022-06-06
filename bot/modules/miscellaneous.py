from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord import app_commands as app
import time

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext


class Miscellaneous(
    commands.Cog,
    name="MODULES.MISCELLANEUS.NAME",
    description="MODULES.MISCELLANEUS.DESCRIPTION",
):
    def __init__(self, bot: Clutter, /) -> None:
        self.bot = bot

    @commands.command(
        aliases=["latency", "pong"],
        brief="COMMANDS.PING.BRIEF",
        help="COMMANDS.PING.HELP",
    )
    @commands.bot_has_permissions(send_messages=True, read_message_history=True)
    async def ping(self, ctx: ClutterContext, /) -> None:
        ts = time.time()
        message = await ctx.reply("** **")
        ts = time.time() - ts
        await message.edit(
            embed=self.bot.embed.info(
                await ctx.i18n("COMMANDS.PING.RESPONSE.TITLE"),
                (await ctx.i18n("COMMANDS.PING.RESPONSE.BODY")).format(
                    ws=int(self.bot.latency * 1000),
                    msg=int(ts * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )

    @app.command(description="COMMANDS.PING.BRIEF")
    async def ping(self, inter: discord.Interaction, /) -> None:
        ts = time.time()
        await inter.response.send_message("** **")
        ts = time.time() - ts
        await inter.edit_original_message(
            embed=self.bot.embed.info(
                await self.bot.i18n(inter, "COMMANDS.PING.RESPONSE.TITLE"),
                (
                    await self.bot.i18n(inter, "COMMANDS.PING.RESPONSE.BODY")
                ).format(
                    ws=int(self.bot.latency * 1000),
                    msg=int(ts * 1000),
                    db=int(await self.bot.db.ping() * 1000),
                ),
            )
        )


async def setup(bot: Clutter, /) -> None:
    await bot.add_cog(Miscellaneous(bot))
