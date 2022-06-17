from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Optional

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from core.bot import Clutter
    from core.context import ClutterContext


class Owner(
    commands.Cog,
    name="MODULES.OWNER.NAME",
    description="MODULES.OWNER.DESCRIPTION",
):
    def __init__(self, bot: Clutter, /) -> None:
        self.bot = bot

    @commands.command(
        brief="COMMANDS.SYNC.BRIEF", help="COMMANDS.SYNC.HELP", hidden=True
    )
    @commands.is_owner()
    @commands.bot_has_permissions(
        send_messages=True, read_message_history=True
    )
    async def sync(
        self,
        ctx: ClutterContext,
        guilds: commands.Greedy[discord.Object],
        spec: Optional[Literal[".", "*"]] = None,
    ) -> None:
        if not guilds:
            if not (guild := ctx.guild):
                raise commands.NoPrivateMessage()

            if spec == ".":
                cmds = await ctx.bot.tree.sync(guild=guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=guild)
                cmds = await ctx.bot.tree.sync(guild=guild)
            else:
                cmds = await ctx.bot.tree.sync()

            await ctx.reply_embed.success(
                await ctx.i18n("COMMANDS.SYNC.RESPONSE.TITLE"),
                (
                    await ctx.i18n(
                        f"COMMANDS.SYNC.RESPONSE.BODY_{'1' if spec else '2'}"
                    )
                ).format(
                    count=len(cmds),
                ),
            )
        else:
            synced = 0
            for guild in guilds:
                try:
                    await ctx.bot.tree.sync(guild=guild)
                except discord.HTTPException:
                    pass
                else:
                    synced += 1

            await ctx.reply_embed.success(
                await ctx.i18n("COMMANDS.SYNC.RESPONSE.TITLE"),
                (await ctx.i18n("COMMANDS.SYNC.RESPONSE.BODY_3")).format(
                    count=synced, total=len(guilds)
                ),
            )


async def setup(bot: Clutter, /) -> None:
    await bot.add_cog(Owner(bot))
