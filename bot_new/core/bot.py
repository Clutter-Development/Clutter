import collections
import pathlib
import time
import traceback
from typing import TYPE_CHECKING, Callable

import aiohttp
import color
import discord
import json5
from core.command_tree import ClutterCommandTree
from core.context import ClutterContext
from discord.ext import commands, tasks
from discord_i18n import DiscordI18N
from discord_utils import QuickEmbedCreator, format_as_list
from mongo_manager import CachedMongoManager

if TYPE_CHECKING:
    from typing_extensions import Self

CURRENT_DIR = pathlib.Path(__file__).resolve().parent


class BotInfo:
    version = "0.0.1"
    github = "https://github.com/Clutter-Development/Clutter"
    discord_url = "https://discord.com/invite/mVKkMZRPQE"
    docs_url = "https://clutter-development.github.io/"
    invite_url: str
    token: str
    default_language: str
    default_prefix: str
    in_development_mode: bool
    start_log: str


class Clutter(commands.AutoShardedBot):
    session: aiohttp.ClientSession
    db: CachedMongoManager
    i18n: DiscordI18N
    error_webhook: discord.Webhook
    log_webhook: discord.Webhook
    uptime: float

    def __init__(self, config: dict, /) -> None:
        self._config = config

        self.info = BotInfo
        self.info.invite_url = discord.utils.oauth_url(
            self.user.id, permissions=discord.Permissions.administrator
        )
        self.info.token = config["BOT_TOKEN"]
        self.info.default_language = config["BOT_DEFAULT_LANGUAGE"]
        self.info.default_prefix = config["BOT_DEFFAULT_PREFIX"]
        self.info.in_development_mode = config["DEVELOPMENT_MODE"]

        self.development_servers = [
            discord.Object(g_id) for g_id in config["BOT_DEVELOPMENT_SERVER_IDS"]
        ]

        self.embed = QuickEmbedCreator(config["STYLE"])

        # Auto spam control for commands.
        # Frequent triggering of this filter (3 or more times in a row) will result in a blacklist.
        self.spam_mapping = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)
        self.spam_counter = collections.Counter()

        super().__init__(
            intents=discord.Intents(
                guilds=True,
                members=True,
                bans=True,
                emojis_and_stickers=True,
                messages=True,
                reactions=True,
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

    async def determine_prefix(
        self, bot: Self, message: discord.Message, /
    ) -> Callable[[Self, discord.Message], list[str]]:
        if guild := message.guild:
            prefix: str = await bot.db.get(
                f"guilds.{guild.id}.prefix", default=self.info.default_prefix
            )
        else:
            prefix = bot.info.default_prefix

        return commands.when_mentioned_or(prefix)

    async def load_extensions(self) -> None:
        loaded = []
        failed = {}
        for fn in map(
            lambda file_path: str(file_path).replace("/", ".")[:-3],
            (CURRENT_DIR / "modules").rglob("*.py"),
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
                    format_as_list(f"Successfully loaded {len(loaded)} modules", "\n".join(loaded))
                )
            )
        log.extend(
            color.red(format_as_list(f"Failed to load {color.bold(name)}", error))
            for name, error in failed.items()
        )

        self.info.start_log = "\n\n".join(log)

    async def on_ready(self) -> None:
        self.uptime = time.time()
        discord_info = format_as_list(
            "Discord Info", f"{color.bold('Version:')} {discord.__version__}"
        )
        bot_info = format_as_list(
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
        print(
            "\n\n".join(
                [
                    self.info.start_log,
                    color.cyan(discord_info),
                    color.magenta(bot_info),
                    color.yellow(f"Running on Clutter v{self.info.version}"),
                ]
            )
        )

    async def on_guild_join(self, guild: discord.Guild, /) -> None:
        if await self.db.get(f"guilds.{guild.id}.blacklisted"):
            await guild.leave()
        elif await self.db.get(f"users.{guild.owner_id}.blacklisted"):
            await guild.leave()
            await self.db.set(f"guilds.{guild.id}.blacklisted", True)  # he he he haw

    @tasks.loop(hours=12)
    async def leave_blacklisted_guilds(self) -> None:
        for guild in self.guilds:
            if await self.db.get(f"guilds.{guild.id}.blacklisted"):
                await guild.leave()
            elif await self.db.get(f"users.{guild.owner_id}.blacklisted"):
                await guild.leave()
                await self.db.set(f"guilds.{guild.id}.blacklisted", True)

    async def blacklist_user(self, user: discord.Object, /) -> bool:
        if await self.db.get(f"users.{user.id}.blacklisted"):
            return False

        await self.db.set(f"users.{user.id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: discord.Object, /) -> bool:
        if not await self.db.get(f"users.{user.id}.blacklisted"):
            return False

        await self.db.set(f"users.{user.id}.blacklisted", False)
        return True

    async def getch_member(self, guild: discord.Guild, user_id: int, /) -> discord.Member | None:
        if (member := guild.get_member(user_id)) is not None:
            return member

        if self.get_shard(guild.shard_id).is_ws_ratelimited():
            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None

        members = await guild.query_members(limit=1, user_ids=[user_id], cache=True)
        return next(iter(members), None)

    def add_command(self, command: commands.Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if not ctx.valid:
            return

        if cog := ctx.command.cog:
            if cog.qualified_name != "Jishaku":
                await ctx.typing()

        await self.invoke(ctx)

    async def get_context(
        self, message: discord.Message, /, cls: type | None = None
    ) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)

    def run(self) -> None:
        async def runner() -> None:
            async with self, aiohttp.ClientSession as session:
                self.session = session
                self.db = CachedMongoManager(
                    self._config["DATABASE_URI"], database="Clutter", max_items=5000
                )
                self.error_webhook = discord.Webhook.from_url(
                    self._config["ERROR_WEBHOOK_URL"], session=session
                )
                self.log_webhook = discord.Webhook.from_url(
                    self._config["LOG_WEBHOOK_URL"], session=session
                )
                self.i18n = DiscordI18N(
                    str(CURRENT_DIR / "translations"),
                    db=self.db,
                    fallback=self.info.default_language,
                )


config = json5.loads((CURRENT_DIR / "config.json5").read_text())
bot = Clutter(config)


@bot.check
async def maintenance_check(ctx: ClutterContext, /) -> bool:
    if bot.info.in_development_mode and not bot.is_owner(ctx.author):
        # TODO: raise error.
        pass
    return False


@bot.check
async def guild_blacklist_check(ctx: ClutterContext, /) -> bool:
    if guild := ctx.guild:
        if await bot.db.get(f"guilds.{guild.id}.blacklisted"):
            await bot.db.set(f"users.{guild.owner_id}.blacklisted", True)
            await guild.leave()
        elif await bot.db.get(f"users.{guild.owner_id}.blacklisted"):
            await bot.db.set(f"guilds.{guild.id}.blacklisted", True)
            await guild.leave()
    return True


@bot.check
async def user_blacklist_check(ctx: ClutterContext, /) -> bool:
    if await bot.db.get(f"users.{ctx.author.id}.blacklisted"):
        # TODO: raise error.
        pass
    return True


@bot.check
async def global_cooldown_check(ctx: ClutterContext, /) -> bool:
    message = ctx.message

    bucket = bot.spam_mapping.get_bucket(message)
    retry_after = bucket.update_rate_limit(message.created_at.timestamp())
