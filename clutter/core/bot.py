import asyncio
import itertools
import os
import pathlib
import time
import traceback

import aiohttp
from discord.utils import oauth_url
from discord import (
    AllowedMentions,
    Guild,
    HTTPException,
    Intents,
    Member,
    Message,
    Object,
    Permissions,
    Webhook,
    __version__ as dpy_version
)
from discord.ext.commands import (
    AutoShardedBot,
    BucketType,
    Command,
    CooldownMapping,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError,
)

from ..utils import color, db, embed, format_as_list, i18n
from .command_tree import ClutterCommandTree
from .context import ClutterContext

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent


class ClutterBot(AutoShardedBot):
    invite_url: str
    start_log: str
    start_time: float

    def __init__(self, config: dict, session: aiohttp.ClientSession, /) -> None:
        self.config = config
        self.session = session

        self.version = "0.0.2"

        self.support_invite = "https://com/invite/mVKkMZRPQE"
        self.documentation_url = "https://clutter-development.github.io/"
        self.source_url = "https://github.com/Clutter-Development/Clutter"

        self.token = config["BOT_TOKEN"]

        self.default_language = config["BOT_DEFAULT_LANGUAGE"]
        self.default_prefix = config["BOT_DEFAULT_PREFIX"]

        # Auto spam control for commands.
        # Frequent triggering of this filter (3 times in a row) will result in a blacklist.
        self.spam_control = type(
            "SpamControl",
        )
        mapping = CooldownMapping.from_cooldown(10, 12, BucketType.user)
        self.spam_control.get_bucket = mapping.get_bucket
        self.spam_control.cooldown = mapping._cooldown

        self.embed = embed.EmbedCreator(config["STYLE"])

        self.db = db.CachedMongoManager(
            config["MONGO_URI"], database="clutter", max_items=5000
        )
        self.i18n = i18n.I18N(
            str(ROOT_DIR / "i18n"),
            db=self.db,
            fallback_language=self.default_language,
        )

        self.error_webhook = Webhook.from_url(
            config["ERROR_WEBHOOK_URL"], session=session
        )
        self.log_webhook = Webhook.from_url(
            config["LOG_WEBHOOK_URL"], session=session
        )

        super().__init__(
            allowed_mentions=AllowedMentions.none(),
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=Intents(
                guilds=True,
                members=True,
                messages=True,
                message_content=True,
            ),
            max_messages=1000,
            owner_ids=set(config["BOT_ADMIN_IDS"]),
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree,
        )

    # Sets the attributes that either need a user instance or needs to be set when the bot starts.

    async def setup_hook(self) -> None:
        self.start_time = time.time()

        self.invite_url = oauth_url(
            self.user.id, permissions=Permissions(administrator=True)
        )

        await self.load_extensions()

    # Gets the bot's uptime in seconds.

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

    # Adds global attributes to commands.

    async def add_command(self, command: Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    # Triggers typing for commands.

    async def process_commands(self, message: Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if not ctx.valid:
            return

        if (cog := ctx.cog) and cog.qualified_name != "Jishaku":
            await ctx.typing()

        await self.invoke(ctx)

    # Custom context.

    async def get_context(self, message: Message, /) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)

    # Blacklist checking.

    async def guild_check(self, guild: Guild, /) -> bool:
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

    async def check_all_guilds(self) -> None:
        await asyncio.gather(
            *(self.guild_check(guild) for guild in self.guilds)
        )

    async def on_guild_join(self, guild: Guild) -> None:
        await self.guild_check(guild)

    async def blacklist_user(self, user: int | Object, /) -> bool:
        user_id = user if isinstance(user, int) else user.id

        if await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: int | Object, /) -> bool:
        user_id = user if isinstance(user, int) else user.id

        if not await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", False)
        return True

    # Gets a member object.

    async def getch_member(
        self, guild: Guild, user_id: int, /
    ) -> Member | None:
        if (member := guild.get_member(user_id)) is not None:
            return member

        if self.get_shard(guild.shard_id).is_ws_ratelimited():
            try:
                return await guild.fetch_member(user_id)
            except HTTPException:
                return None

        if members := await guild.query_members(
            limit=1, user_ids=[user_id], cache=True
        ):
            return members[0]

    # Loads all the cogs.

    async def load_extensions(self) -> None:
        loaded = []
        failed = {}
        for fn in itertools.chain(
            map(
                lambda fp: ".".join(fp.parts)[:-3],
                (ROOT_DIR / "cogs").relative_to(os.getcwd()).rglob("*.py"),
            ),
            ["jishaku"],
        ):
            try:
                await self.load_extension(fn)
                loaded.append(fn.rsplit(".", 1)[-1])
            except (
                ExtensionFailed,
                NoEntryPointError,
                ExtensionNotFound,
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

        self.start_log = "\n\n".join(log)

    async def on_ready(self) -> None:
        print(
            "\n\n".join(
                [
                    self.start_log,
                    color.cyan(
                        format_as_list(
                            "Discord Info",
                            f"{color.bold('Version:')} {dpy_version}",
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
                    color.yellow(f"Running on Clutter v{self.version}"),
                ]
            )
        )
