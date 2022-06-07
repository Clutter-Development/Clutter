from __future__ import annotations

import asyncio
import collections
import itertools
import os
import pathlib
import time
import traceback
from typing import TYPE_CHECKING

import aiohttp
import color
import discord
import json5
from core.errors import UserHasBeenBlacklisted, UserIsBlacklisted, BotInMaintenance
from core.command_tree import ClutterCommandTree
from core.context import ClutterContext
from discord.ext import commands, tasks
from discord_i18n import DiscordI18N
from discord_utils import QuickEmbedCreator, format_as_list
from mongo_manager import CachedMongoManager

if TYPE_CHECKING:
    from typing_extensions import Self

BOT_DIR = pathlib.Path(__file__).resolve().parent.parent


class SpamControl:
    mapping = commands.CooldownMapping.from_cooldown(
        10, 12, commands.BucketType.user
    )
    counter = collections.Counter()


class BotInfo:
    default_language: str
    default_prefix: str
    discord_invite_url = "https://discord.com/invite/mVKkMZRPQE"
    documentation_url = "https://clutter-development.github.io/"
    github_repository_url = "https://github.com/Clutter-Development/Clutter"
    invite_url: str
    is_in_development_mode: bool
    start_log: str
    token: str
    uptime: float
    version = "0.1.0"

    def __init__(self, config: dict, /) -> None:
        self.bot_token = config["BOT_TOKEN"]
        self.default_language = config["BOT_DEFAULT_LANGUAGE"]
        self.default_prefix = config["BOT_DEFAULT_PREFIX"]
        self.is_in_development_mode = config["DEVELOPMENT_MODE"]


class Clutter(commands.AutoShardedBot):
    db: CachedMongoManager
    error_webhook: discord.Webhook
    i18n: DiscordI18N
    log_webhook: discord.Webhook
    session: aiohttp.ClientSession
    tree: ClutterCommandTree
    user: discord.ClientUser

    def __init__(self, config: dict, /) -> None:
        self.config = config
        self.info = BotInfo(config)

        self.development_servers = [
            discord.Object(g_id) for g_id in config["BOT_DEVELOPMENT_GUILD_IDS"]
        ]

        self.embed = QuickEmbedCreator(config["STYLE"])

        # Auto spam control for commands.
        # Frequent triggering of this filter (3 or more times in a row) will result in a blacklist.
        self.spam_control = SpamControl()

        super().__init__(
            intents=discord.Intents(
                guilds=True,
                members=True,
                bans=True,
                emojis_and_stickers=True,
                messages=True,
                guild_reactions=True,
                message_content=True,
            ),
            command_prefix=self.determine_prefix,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions.none(),
            max_messages=1000,
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree,
            owner_ids=set(config["BOT_ADMIN_IDS"]),
        )

    # Overrides.

    def add_command(self, command: commands.Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if not ctx.command:
            return

        if (cog := ctx.command.cog) and cog.qualified_name != "Jishaku":
            await ctx.typing()

        await self.invoke(ctx)

    async def get_context(
        self, message: discord.Message, /, cls: type | None = None
    ) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)

    def run(self) -> None:
        async def runner() -> None:
            async with self, aiohttp.ClientSession() as session:
                self.session = session
                self.db = CachedMongoManager(
                    self.config["DATABASE_URI"],
                    database="Clutter",
                    max_items=5000,
                )
                self.error_webhook = discord.Webhook.from_url(
                    self.config["ERROR_WEBHOOK_URL"], session=session
                )
                self.log_webhook = discord.Webhook.from_url(
                    self.config["LOG_WEBHOOK_URL"], session=session
                )
                self.i18n = DiscordI18N(
                    str(BOT_DIR / "translations"),
                    db=self.db,
                    fallback=self.info.default_language,
                )
                self.leave_blacklisted_guilds.start()
                await self.load_extensions()
                await self.start(self.info.bot_token, reconnect=True)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            self.leave_blacklisted_guilds.cancel()

    # Blacklist-checking stuff.

    async def on_guild_join(self, guild: discord.Guild, /) -> bool:
        if await self.db.get(f"guilds.{guild.id}.blacklisted"):
            await asyncio.gather(
                guild.leave(),
                self.db.set(f"users.{guild.owner_id}.blacklisted", True),
            )
            return False
        elif await self.db.get(f"users.{guild.owner_id}.blacklisted"):
            await asyncio.gather(
                guild.leave(),
                self.db.set(f"guilds.{guild.id}.blacklisted", True),
            )
            return False
        return True  # True means the guild is safe.

    @tasks.loop(hours=12)  # Might remove this.
    async def leave_blacklisted_guilds(self) -> None:
        await asyncio.gather(
            *(self.on_guild_join(guild) for guild in self.guilds)
        )

    async def blacklist_user(self, user: int | discord.Object, /) -> bool:
        user_id = user if isinstance(user, int) else user.id
        if await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: int | discord.Object, /) -> bool:
        user_id = user if isinstance(user, int) else user.id
        if not await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", False)
        return True

    # Others.

    async def determine_prefix(
        self, _: Self, message: discord.Message, /
    ) -> list[str]:
        return [
            await self.db.get(
                f"guilds.{guild.id}.prefix", default=self.info.default_prefix
            )
            if (guild := message.guild)
            else self.info.default_prefix,
            f"<@{self.user.id}>",
            f"<@!{self.user.id}>",
        ]

    async def getch_member(
        self, guild: discord.Guild, user_id: int, /
    ) -> discord.Member | None:
        if (member := guild.get_member(user_id)) is not None:
            return member

        if self.get_shard(guild.shard_id).is_ws_ratelimited():
            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None

        if members := await guild.query_members(
            limit=1, user_ids=[user_id], cache=True
        ):
            return members[0]

    async def load_extensions(self) -> None:
        loaded = []
        failed = {}
        for fn in itertools.chain(
            map(
                lambda fp: ".".join(fp.parts)[:-3],
                (BOT_DIR / "modules").relative_to(os.getcwd()).rglob("*.py"),
            ),
            ["jishaku"],
        ):
            try:
                await self.load_extension(fn)
                loaded.append(fn.rsplit(".", 1)[-1])
            except (
                commands.ExtensionFailed,
                commands.NoEntryPointError,
                commands.ExtensionNotFound,
            ):
                failed[fn.rsplit(".", 1)[-1]] = traceback.format_exc()

        log = []
        if loaded:
            log.append(
                color.green(
                    format_as_list(
                        f"Successfully loaded {len(loaded)} modules",
                        "\n".join(loaded),
                    )
                )
            )
        log.extend(
            color.red(
                format_as_list(f"Failed to load {color.bold(name)}", error)
            )
            for name, error in failed.items()
        )

        self.info.start_log = "\n\n".join(log)

    async def on_ready(self) -> None:
        self.info.uptime = time.time()
        self.info.bot_invite_url = discord.utils.oauth_url(
            self.user.id, permissions=discord.Permissions(administrator=True)
        )
        print(
            "\n\n".join(
                [
                    self.info.start_log,
                    color.cyan(
                        format_as_list(
                            "Discord Info",
                            f"{color.bold('Version:')} {discord.__version__}",
                        )
                    ),
                    color.magenta(
                        format_as_list(
                            "Bot Info",
                            "\n".join(
                                [
                                    f"{color.bold('User:')} {self.user}",
                                    f"{color.bold('ID:')} {self.user.id}",
                                    f"{color.bold('Total Guilds:')} {len(self.guilds)}",
                                    f"{color.bold('Total Users:')} {len(self.users)}",
                                    f"{color.bold('Total Shards:')} {self.shard_count}",
                                ]
                            ),
                        )
                    ),
                    color.yellow(f"Running on Clutter v{self.info.version}"),
                ]
            )
        )


bot = Clutter(json5.loads((BOT_DIR / "config.json5").read_text()))


# Base checks.


@bot.check
@bot.tree.check
async def maintenance_check(
    ctx: ClutterContext | discord.Interaction, /
) -> bool:
    if bot.info.is_in_development_mode and not await bot.is_owner(
        ctx.author if isinstance(ctx, ClutterContext) else ctx.user
    ):
        raise BotInMaintenance(
            "The bot is currently in maintenance. Only bot admins can use commands."
        )
    return True


@bot.check
@bot.tree.check
async def guild_blacklist_check(
    ctx: ClutterContext | discord.Interaction, /
) -> bool:
    return await bot.on_guild_join(guild) if (guild := ctx.guild) else True


@bot.check
@bot.tree.check
async def user_blacklist_check(
    ctx: ClutterContext | discord.Interaction, /
) -> bool:
    author = ctx.author if isinstance(ctx, ClutterContext) else ctx.user
    if not await bot.is_owner(author) and await bot.db.get(
        f"users.{author.id}.blacklisted"
    ):
        raise UserIsBlacklisted(
            "You are blacklisted from using this bot. retard."
        )
    return True


@bot.check
# TODO: @bot.tree.check
async def global_cooldown_check(ctx: ClutterContext, /) -> bool:
    if await bot.is_owner(ctx.author):
        return True

    message = ctx.message
    author_id = ctx.author.id

    spam = bot.spam_control
    counter = spam.counter

    if not (
        retry_after := spam.mapping.get_bucket(message).update_rate_limit(message.created_at.timestamp())
    ):
        return True

    counter[author_id] += 1

    if counter[author_id] < 3:
        raise commands.CommandOnCooldown(
            spam.mapping._cooldown,
            retry_after,
            commands.BucketType.user,
        )

    await bot.blacklist_user(author_id)
    del counter[author_id]

    author = ctx.author

    # Sends info to the log webhook.
    embed = bot.embed.warning(
        f"**{author}** has been blacklisted for spamming!",
        f"Incident time: <t:{int(time.time())}:F>",
    ).add_field(
        title="User Info",
        description=f"**Mention:** {author.mention}\n**Tag:** {author}\n**ID:** {author.id}",
    )
    if guild := ctx.guild:
        channel = ctx.channel
        embed.add_field(
            title="Guild Info",
            description=f"**Name:** {guild.name}\n**ID:** {guild.id}\n[Jump!](https://discord.com/channels/{guild.id})",
        ).add_field(
            title="Channel Info",
            description=f"**Mention:** {channel.mention}\n**Name:** {channel.name}\n**ID:** {channel.id}\n[Jump!]({channel.jump_url})",
        )

    asyncio.create_task(bot.log_webhook.send(embed=embed))
    raise UserHasBeenBlacklisted(
        "You have been blacklisted for spamming commands."
    )
