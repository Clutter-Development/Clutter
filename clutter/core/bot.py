from __future__ import annotations

from asyncio import create_task, gather
from collections import Counter
from itertools import chain
from pathlib import Path
from re import MULTILINE, search
from time import time
from traceback import format_exc
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
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
    __version__ as dpy_version,
)
from discord.ext.commands import (
    AutoShardedBot,
    BucketType,
    Command,
    CommandOnCooldown,
    CooldownMapping,
    ExtensionFailed,
    ExtensionNotFound,
    NoEntryPointError,
)
from discord.utils import oauth_url
from json5 import loads

from ..utils import color, format_as_list
from ..utils.db import CachedMongoManager
from ..utils.embed import EmbedCreator
from ..utils.i18n import I18N
from .command_tree import ClutterCommandTree
from .context import ClutterContext
from .errors import UserHasBeenBlacklisted, UserIsBlacklisted

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from typing_extensions import Self

    from .interaction import ClutterInteraction

__all__ = ("ClutterBot",)

ROOT_DIR = Path(__file__).resolve().parent.parent


class ClutterBot(AutoShardedBot):
    invite_url: str
    start_log: str
    start_time: float
    tree: ClutterCommandTree

    def __init__(self, config: dict, session: ClientSession) -> None:
        self.config = config
        self.session = session

        self.version = search(  # type: ignore
            r'^version\s*=\s*["]([^"]*)["]',
            (ROOT_DIR.parent / "pyproject.toml").read_text(),
            MULTILINE,
        )[1]

        self.support_invite = "https://com/invite/mVKkMZRPQE"
        self.documentation_url = "https://clutter-development.github.io/"
        self.source_url = "https://github.com/Clutter-Development/Clutter"

        self.token = config["BOT_TOKEN"]

        self.default_language = config["BOT_DEFAULT_LANGUAGE"]
        self.default_prefix = config["BOT_DEFAULT_PREFIX"]

        # Auto spam control for commands.
        # Frequent triggering of this filter (3 times in a row) will result in a blacklist.
        mapping = CooldownMapping.from_cooldown(10, 12, BucketType.user)

        class SpamControl:
            # noinspection PyProtectedMember
            cooldown = mapping._cooldown
            get_bucket = mapping.get_bucket
            counter = Counter()

        self.spam_control = SpamControl()

        self.embed = EmbedCreator(config["STYLE"])

        self.db = CachedMongoManager(
            config["MONGO_URI"], database="clutter", max_items=5000
        )
        self.i18n = I18N(
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
            command_prefix=self.get_prefix,  # type: ignore
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

    async def setup_hook(self) -> None:
        self.start_time = time()

        self.invite_url = oauth_url(
            self.user.id, permissions=Permissions(administrator=True)  # type: ignore
        )

        await self.load_extensions()

    @property
    def uptime(self) -> float:
        return time() - self.start_time

    def add_command(self, command: Command) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    async def process_commands(self, message: Message) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if not ctx.valid:
            return

        if ctx.cog and ctx.cog.qualified_name != "Jishaku":
            await ctx.typing()

        await self.invoke(ctx)

    async def get_prefix(self, message: Message) -> list[str]:
        if message.guild:
            prefix = await self.db.get(
                f"guilds.{message.guild.id}.prefix", default=self.default_prefix
            )
        else:
            prefix = self.default_prefix

        return [prefix, f"<@{self.user.id}>", f"<@!{self.user.id}>"]  # type: ignore

    # noinspection PyMethodOverriding
    async def get_context(self, message: Message) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)

    async def guild_check(self, guild: Guild) -> bool:
        if await self.db.get(f"guilds.{guild.id}.blacklisted"):
            await gather(
                guild.leave(),
                self.db.set(f"users.{guild.owner_id}.blacklisted", True),
            )
            return False
        elif await self.db.get(f"users.{guild.owner_id}.blacklisted"):
            await gather(
                guild.leave(),
                self.db.set(f"guilds.{guild.id}.blacklisted", True),
            )
            return False
        return True  # True means the guild is safe.

    async def check_all_guilds(self) -> None:
        await gather(*(self.guild_check(guild) for guild in self.guilds))

    async def on_guild_join(self, guild: Guild) -> None:
        await self.guild_check(guild)

    async def blacklist_user(self, user: int | Object) -> bool:
        user_id = user if isinstance(user, int) else user.id

        if await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: int | Object) -> bool:
        user_id = user if isinstance(user, int) else user.id

        if not await self.db.get(f"users.{user_id}.blacklisted"):
            return False

        await self.db.set(f"users.{user_id}.blacklisted", False)
        return True

    async def getch_member(self, guild: Guild, user_id: int) -> Member | None:
        if (member := guild.get_member(user_id)) is not None:
            return member

        if self.get_shard(guild.shard_id).is_ws_ratelimited():  # type: ignore
            try:
                return await guild.fetch_member(user_id)
            except HTTPException:
                return None

        if members := await guild.query_members(
            limit=1, user_ids=[user_id], cache=True
        ):
            return members[0]

    async def load_extensions(self) -> None:
        loaded = []
        failed = {}
        cog_dir = ROOT_DIR / "cogs"
        for fn in chain(
            map(
                lambda fp: f"clutter.cogs.{'.'.join(fp.relative_to(cog_dir).parts)[:-3]}",
                cog_dir.rglob("*.py"),
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
                failed[fn.rsplit(".", 1)[-1]] = format_exc()

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
                                    f"{color.bold('ID:')} {self.user.id}",  # type: ignore
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

    async def __aexit__(self, *args: Any):
        await self.close()
        await self.session.close()

    @classmethod
    async def init(cls) -> Self:
        bot = cls(
            loads((ROOT_DIR / "config.json5").read_text()), ClientSession()
        )

        @bot.check
        @bot.tree.check
        async def guild_blacklist_check(
            ctx: ClutterContext | ClutterInteraction,
        ) -> bool:
            # noinspection PyTypeChecker
            return (
                (
                    await bot.is_owner(ctx.guild.owner)
                    if ctx.guild.owner
                    else False
                )
                or await bot.guild_check(ctx.guild)
                if ctx.guild
                else True
            )

        @bot.check
        @bot.tree.check
        async def user_blacklist_check(
            ctx: ClutterContext | ClutterInteraction,
        ) -> bool:
            if not await bot.is_owner(ctx.author) and await bot.db.get(
                f"users.{ctx.author.id}.blacklisted"
            ):
                raise UserIsBlacklisted("You are banned from using this bot.")
            return True

        @bot.check
        # TODO: @bot.tree.check
        async def global_cooldown_check(ctx: ClutterContext) -> bool:
            author = ctx.author

            if await bot.is_owner(author):
                return True

            author_id = author.id
            counter = bot.spam_control.counter

            if not (
                retry_after := bot.spam_control.get_bucket(
                    ctx.message
                ).update_rate_limit(  # type: ignore
                    ctx.message.created_at.timestamp()
                )
            ):
                return True

            counter[author_id] += 1

            if counter[author_id] < 3:
                raise CommandOnCooldown(
                    bot.spam_control.cooldown, retry_after, BucketType.user  # type: ignore
                )

            await bot.blacklist_user(author_id)
            del counter[author_id]

            embed = bot.embed.warning(
                f"**{author}** has been blacklisted for spamming!",
                f"Incident time: <t:{int(time())}:F>",
            ).add_field(
                title="User Info",
                description=(
                    f"**Mention:** {author.mention}\n**Tag:**"
                    f" {author}\n**ID:** {author.id}"
                ),
            )
            if ctx.guild:
                channel = ctx.channel
                embed.add_field(
                    title="Guild Info",
                    description=(
                        f"**Name:** {ctx.guild.name}\n**ID:**"
                        f" {ctx.guild.id}\n[Jump!](https://discord.com/channels/{ctx.guild.id})"
                    ),
                ).add_field(
                    title="Channel Info",
                    description=f"**Mention:** {channel.mention}\n**Name:** {channel.name}\n**ID:** {channel.id}\n[Jump!]({channel.jump_url})",  # type: ignore
                )

            create_task(bot.log_webhook.send(embed=embed))
            raise UserHasBeenBlacklisted(
                "You have been blacklisted for spamming commands."
            )

        return bot
