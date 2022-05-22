import asyncio
import collections
import math
import os
import pathlib
import time
import traceback

import aiohttp
import discord
import json5
from core.command_tree import ClutterCommandTree
from core.context import ClutterContext
from discord.ext import commands, tasks
from utils import I18N, CachedMongoManager, EmbedBuilder, color, errors, listify

BASE_PATH = "./" if os.getenv("USING_DOCKER") else "./bot/"


class Clutter(commands.AutoShardedBot):
    tree: ClutterCommandTree
    user: discord.ClientUser

    def __init__(self, config: dict, /):
        """Initialize the bot itself.

        Args:
            config (dict): The bot configuration
        """
        self.session = aiohttp.ClientSession()

        self.config = config
        bot_cfg = config["BOT"]
        db_cfg = config["DATABASE"]

        # Properties
        self.token = bot_cfg["TOKEN"]
        self.admin_ids = set(bot_cfg["ADMIN_IDS"])
        self.version = bot_cfg["VERSION"]
        self.github = bot_cfg["GITHUB_REPO_URL"]
        self.discord_invite = bot_cfg["DISCORD_INVITE_URL"]
        self.documentation_url = bot_cfg["DOCUMENTATION_URL"]
        self.invite_url = bot_cfg["INVITE_URL"]
        self.default_prefix = bot_cfg["DEFAULT_PREFIX"]
        self.default_language = bot_cfg["DEFAULT_LANGUAGE"]
        self.in_development = bot_cfg["DEVELOPMENT_MODE"]

        self.development_servers = [
            discord.Object(id=g_id) for g_id in bot_cfg["DEVELOPMENT_SERVER_IDS"]
        ]

        # Classes
        self.db = CachedMongoManager(
            db_cfg["URI"],
            database=db_cfg["NAME"],
            cooldown=db_cfg["CACHE_COOLDOWN"],
        )
        self.error_webhook = discord.Webhook.from_url(
            bot_cfg["ERROR_WEBHOOK_URL"], session=self.session, bot_token=self.token
        )
        self.log_webhook = discord.Webhook.from_url(
            bot_cfg["LOG_WEBHOOK_URL"], session=self.session, bot_token=self.token
        )
        self.embed = EmbedBuilder(self)
        self.i18n = I18N(self, os.path.abspath(f"{BASE_PATH}i18n"))

        # Auto spam control for commands
        # Frequent triggering of this filter (3 or more times in a row) will result in a blacklist
        self.spam_control = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)
        self.spam_counter = collections.Counter()

        self.uptime = 0
        self.startup_log = ""

        intents = discord.Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis_and_stickers=True,
            messages=True,
            reactions=True,
            message_content=True,
        )

        stuff_to_cache = discord.MemberCacheFlags.from_intents(intents)
        allowed_mentions = discord.AllowedMentions.none()
        super().__init__(
            intents=intents,
            command_prefix=self.determine_prefix,
            case_insensitive=True,
            help_command=None,
            allowed_mentions=allowed_mentions,
            member_cache_flags=stuff_to_cache,
            chunk_guilds_at_startup=True,
            max_messages=1000,
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree,
            owner_ids=self.admin_ids,
        )

    # ---- Library-Used Attributes  ---- #
    # -- No Docstrings Since Lib Used -- #

    async def startup_hook(self) -> None:
        await self.load_extensions()
        print(self.startup_log)

    async def determine_prefix(
        self, bot_: commands.AutoShardedBot, message: discord.Message, /
    ) -> list[str]:
        if guild := message.guild:
            prefix = await self.db.get(
                f"guilds.{guild.id}.prefix", default=self.default_prefix, cache_forever=True
            )
            return commands.when_mentioned_or(prefix)(bot_, message)
        return commands.when_mentioned_or(self.default_prefix)(bot_, message)

    # -- GateWay Events -- #
    # -- Same As Above  -- #

    async def on_ready(self) -> None:
        self.uptime = math.floor(time.time())
        discord_info = listify("Discord Info", f"{color.bold('Version:')} {discord.__version__}")
        bot_info = listify(
            "Bot Info",
            "\n".join(
                [
                    f"{color.bold('User:')} {self.user}",
                    f"{color.bold('ID:')} {self.user.id}",
                    f"{color.bold('Total Guilds:')} {len(self.guilds)}",
                    f"{color.bold('Total Users:')} {len(self.users)}",
                    f"{color.bold('Total Shards: ')} {self.shard_count}",
                ]
            ),
        )
        print(
            "\n\n".join(
                [
                    color.cyan(discord_info),
                    color.magenta(bot_info),
                    color.yellow(f"Running on Clutter v{self.version}"),
                ]
            )
        )

    async def on_guild_join(self, guild: discord.Guild) -> None:
        if await self.db.get(f"guilds.{guild.id}.blacklisted", default=False, cache_forever=True):
            await guild.leave()

    # -- Tasks -- #

    @tasks.loop(hours=12)
    async def leave_blacklisted_guilds(self) -> None:
        for guild in self.guilds:
            if await self.db.get(
                f"guilds.{guild.id}.blacklisted", default=False, cache_forever=True
            ):
                await guild.leave()

    # -- Custom Attributes -- #

    async def load_extensions(self) -> None:
        """Loads all the extensions in the ./modules directory and sets the self.startup_log."""
        loaded = []
        failed = {}
        for fn in map(
            lambda file_path: str(file_path).replace(os.pathsep, ".")[:-3],
            pathlib.Path("./modules").rglob("*.py"),
        ):
            try:
                await self.load_extension(fn)
                loaded.append(fn)
            except (commands.ExtensionFailed, commands.NoEntryPointError):
                failed[fn] = traceback.format_exc()
        log = []
        if loaded:
            log.append(
                color.green(
                    listify(f"Successfully loaded {len(loaded)} modules", "\n".join(loaded))
                )
            )
        log.extend(
            color.red(listify(f"Failed to load {color.bold(name)}", error))
            for name, error in failed.items()
        )

        self.startup_log = "\n".join(log)

    async def blacklist_user(self, user: discord.User | discord.Member | int, /) -> bool:
        """Blacklists a user.

        Args:
            user (discord.User | discord.Member | int): The user (user_id) to blacklist.

        Returns:
            bool: Wheter or not the user was blacklisted.
        """
        user_id = user if isinstance(user, int) else user.id
        if await self.db.get(f"users.{user_id}.blacklisted", default=False, cache_forever=True):
            return False
        await self.db.set(f"users.{user_id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: discord.User | discord.Member | int, /) -> bool:
        """Unblacklists a user.

        Args:
            user (discord.User | discord.Member | int): The user (user_id) to unblacklist.

        Returns:
            bool: Wheter or not the user was unblacklisted.
        """
        user_id = user if isinstance(user, int) else user.id
        if not await self.db.get(f"users.{user_id}.blacklisted", default=False, cache_forever=True):
            return False
        await self.db.set(f"users.{user_id}.blacklisted", False)
        return True

    async def log_spammer(self, ctx: commands.Context, /) -> None:
        """Logs a spammer.

        Args:
            ctx (commands.Context): The context to use.
        """
        embed = self.embed.warning(f"**{ctx.author}** has been blacklisted for spamming!")  # type: ignore
        embed.add_field(
            name="User Info",
            value=f"**Mention:** {ctx.author.mention}\n**Tag:** {ctx.author}\n**ID:** {ctx.author.id}",
        )
        if guild := ctx.guild:
            embed.add_field(
                name="Guild Info",
                value=f"**Name:** {guild.name}\n**ID:** {guild.id}\n[Jump to Guild](https://discord.com/channels/{guild.id})",
            )
            embed.add_field(
                name="Channel Info",
                value=f"**Mention:** {ctx.channel.mention}\n**Name:** {ctx.channel.name}\n**ID:** {ctx.channel.id}\n[Jump to channel]({ctx.channel.jump_url})",
                # type: ignore
            )
        await self.log_webhook.send(embed=embed)

    async def getch_member(self, guild: discord.Guild, user_id: int, /) -> discord.Member | None:
        """Gets a member from the cache, if it doesn't exist, it fetches it via the gateway or http.

        Args:
            guild (discord.Guild): The guild to get the member from.
            user_id (int): The user_id that belongs to the member

        Returns:
            discord.Member | None: The member.
        """
        if (member := guild.get_member(user_id)) is not None:
            return member
        if self.get_shard(guild.shard_id).is_ws_ratelimited():  # type: ignore
            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None

        members = await guild.query_members(limit=1, user_ids=[user_id], cache=True)
        if not members:
            return None
        return members[0]

    # -- Overrides -- #
    # -- No DocStr -- #

    def run(self) -> None:
        try:
            super().run(self.token, reconnect=True)
        finally:

            async def stop():
                await self.session.close()

            asyncio.run(stop())

    def add_command(self, command: commands.Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return
        ctx = await self.get_context(message)
        if ctx.command is None:
            return
        if cog := ctx.command.cog:
            if cog.qualified_name != "Jishaku":
                await ctx.typing()
        await self.invoke(ctx)

    async def get_context(
        self, message: discord.Message, /, cls: type | None = None
    ) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)


with open(f"{BASE_PATH}config.json5") as f:
    bot = Clutter(json5.load(f))


# -- Base Checks For Traditional Commands-- #


@bot.check
async def maintenance_check(ctx: ClutterContext, /) -> bool:
    if bot.in_development and not bot.is_owner(ctx.author):
        raise errors.InDevelopmentMode(
            "This bot is currently in development mode. Only bot admins can use commands."
        )
    return True


@bot.check
async def user_blacklist_check(ctx: ClutterContext, /) -> bool:
    if bot.db.get(f"users.{ctx.author.id}.blacklisted", default=False, cache_forever=True):
        raise errors.UserIsBlacklisted("You are blacklisted from using this bot.")
    return True


@bot.check
async def guild_blacklist_check(ctx: ClutterContext, /) -> bool:
    if guild := ctx.guild:
        if bot.db.get(f"guilds.{guild.id}.blacklisted", default=False, cache_forever=True):
            raise errors.GuildIsBlacklisted("This guild is blacklisted from using this bot.")
    return True


@bot.check
async def global_cooldown_check(ctx: ClutterContext, /) -> bool:
    bucket = bot.spam_control.get_bucket(ctx.message)
    ts = ctx.message.created_at.timestamp()
    retry_after = bucket.update_rate_limit(ts)
    author_id = ctx.message.author.id
    if retry_after and not bot.is_owner(ctx.author):
        bot.spam_counter[author_id] += 1
        if bot.spam_counter[author_id] >= 3:
            await bot.blacklist_user(author_id)
            del bot.spam_counter[author_id]
            await bot.log_spammer(ctx)
            raise errors.UserHasBeenBlacklisted(
                "You have been blacklisted from using this bot for exessive command spam."
            )
        raise errors.GlobalCooldownReached(retry_after, "Global command cooldown has been reached")
    bot.spam_counter.pop(author_id, None)
    return True


# -- Base Checks For Application Commands -- #


@bot.tree.check
async def app_maintenance_check(inter: discord.Interaction, /) -> bool:
    if bot.in_development and not bot.is_owner(inter.user):
        raise errors.InDevelopmentMode(
            "This bot is currently in development mode. Only bot admins can use commands."
        )
    return True


@bot.tree.check
async def app_user_blacklist_check(inter: discord.Interaction, /) -> bool:
    if bot.db.get(f"users.{inter.user.id}.blacklisted", default=False, cache_forever=True):
        raise errors.UserIsBlacklisted("You are blacklisted from using this bot.")
    return True


@bot.tree.check
async def app_guild_blacklist_check(inter: discord.Interaction, /) -> bool:
    if guild_id := inter.guild_id:
        if bot.db.get(f"guilds.{guild_id}.blacklisted", default=False, cache_forever=True):
            raise errors.GuildIsBlacklisted("This guild is blacklisted from using this bot.")
    return True


@bot.tree.check
async def app_global_cooldown_check(inter: discord.Interaction, /) -> bool:
    return True  # TODO: implement global cooldown for application commands
