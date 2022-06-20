from __future__ import annotations

from time import monotonic
from typing import TYPE_CHECKING

from discord import Member, User
from discord.app_commands import command as slash_command
from discord.ext.commands import Cog, command

if TYPE_CHECKING:
    from ..core import ClutterBot, ClutterContext, ClutterInteraction
    from ..utils.embed import Embed


class Miscellaneous(
    Cog,
    name="COGS.MISCELLANEOUS.NAME",
    description="COGS.MISCELLANEOUS.DESCRIPTION",
):
    def __init__(self, bot: ClutterBot) -> None:
        self.bot = bot

    @command(
        aliases=("latency",),
        brief="COMMANDS.PING.BRIEF",
        help="COMMANDS.PING.HELP",
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

    @slash_command(name="ping", description="COMMANDS.PING.BRIEF")  # type: ignore
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

    async def create_info_embed(
        self,
        ctx: ClutterContext | ClutterInteraction,
        user: User | Member | None,
    ) -> Embed:
        if not user:
            user = ctx.author
        is_member = isinstance(user, Member)
        embed = self.bot.embed.info(
            await ctx.i18n("COMMANDS.INFO.RESPONSE.TITLE", user=user),
            await ctx.i18n(
                "COMMANDS.INFO.RESPONSE.BODY",
                id=user.id,
                created_at=f"<t:{int(user.created_at.timestamp())}:F>",
            )
            + (
                "\n"
                + await ctx.i18n(
                    "COMMANDS.INFO.RESPONSE.JOINED_AT",
                    joined_at=f"<t:{int(user.joined_at.timestamp())}:F>",
                )
                if is_member
                else ""
            ),
        ).set_thumbnail(url=user.display_avatar.url)

        if is_member and (roles := user.roles):
            embed.add_field(
                await ctx.i18n("COMMANDS.INFO.FIELDS.ROLES"),
                ", ".join(
                    role.mention
                    for role in roles
                    if not role == ctx.guild.default_role
                ),
            )

        return embed

    @command(
        aliases=("userinfo", "user-info", "user_info"),
        brief="COMMANDS.INFO.BRIEF",
        help="COMMANDS.INFO.HELP",
    )
    async def info(
        self, ctx: ClutterContext, user: User | Member | None = None
    ) -> None:
        await ctx.reply(embed=await self.create_info_embed(ctx, user))

    @slash_command(
        name="info",
        description="COMMANDS.INFO.BRIEF",
    )
    async def slash_info(
        self, ctx: ClutterInteraction, user: Member | None = None
    ) -> None:
        await ctx.reply(embed=await self.create_info_embed(ctx, user))


async def setup(bot: ClutterBot) -> None:
    await bot.add_cog(Miscellaneous(bot))
