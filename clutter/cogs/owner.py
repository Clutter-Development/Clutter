from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

import discord
from discord.ext.commands import (
    Cog,
    Greedy,
    NoPrivateMessage,
    command,
    is_owner,
)

if TYPE_CHECKING:
    from ..core import ClutterBot, ClutterContext


class Owner(
    Cog,
    name="COGS.OWNER.NAME",
    description="COGS.OWNER.DESCRIPTION",
):
    def __init__(self, bot: ClutterBot) -> None:
        self.bot = bot

    @command(
        brief="COMMANDS.SYNC.BRIEF", help="COMMANDS.SYNC.HELP", hidden=True
    )
    @is_owner()
    async def sync(
        self,
        ctx: ClutterContext,
        guilds: Greedy[discord.Object],
        spec: Optional[Literal[".", "*"]] = None,
    ) -> None:
        if not guilds:
            if not (guild := ctx.guild) and not spec:
                raise NoPrivateMessage()

            if spec == ".":
                commands = await self.bot.tree.sync(guild=guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=guild)
                commands = await self.bot.tree.sync(guild=guild)
            else:
                commands = await self.bot.tree.sync()

            await ctx.reply_embed.success(
                await ctx.i18n("COMMANDS.SYNC.RESPONSE.TITLE"),
                await ctx.i18n(
                    f"COMMANDS.SYNC.RESPONSE.BODY_{'1' if spec else '2'}",
                    count=len(commands),
                ),
            )
        else:
            synced = 0
            for guild in guilds:
                try:
                    await self.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    pass
                else:
                    synced += 1

            await ctx.reply_embed.success(
                await ctx.i18n("COMMANDS.SYNC.RESPONSE.TITLE"),
                await ctx.i18n(
                    "COMMANDS.SYNC.RESPONSE.BODY_3",
                    success=synced,
                    total=len(guilds),
                ),
            )


async def setup(bot: ClutterBot) -> None:
    await bot.add_cog(Owner(bot))
