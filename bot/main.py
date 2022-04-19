import asyncio
import collections
import math
import os
import pathlib
import sys
import time
import traceback
from typing import List, Optional, Type, Union

import aiohttp
import discord
import json5
from core.context import ClutterContext
from core.slash_tree import ClutterCommandTree
from discord.ext import commands
from discord.ext.commands._types import ContextT  # noqa: 12
from dotenv import load_dotenv
from utils import CachedMongoManager, CommandChecks, EmbedBuilder, color, listify

os.system("cls" if sys.platform == "win32" else "clear")


class Clutter(commands.AutoShardedBot):
    def __init__(self):
        self.session = aiohttp.ClientSession()

        # load config
        with open("./config.json5") as f:
            self.config = json5.load(f)

        # get critical info
        if self.config.get("USE_ENV", False):
            load_dotenv()
            self.token = os.getenv("BOT_TOKEN")
            webhook_url = os.getenv("ERROR_WEBHOOK_URL")
            db_uri = os.getenv("DATABASE_URI")
        else:
            self.token = self.config["BOT"]["TOKEN"]
            webhook_url = self.config["BOT"]["ERROR_WEBHOOK_URL"]
            db_uri = self.config["DATABASE"]["URI"]

        # initialize webhook and database
        self.webhook = discord.Webhook.from_url(webhook_url, session=self.session)
        self.db = CachedMongoManager(
            db_uri,
            database=self.config["DATABASE"]["NAME"],
            cooldown=self.config["DATABASE"]["CACHE_COOLDOWN"],
        )

        # initialize EmbedBuilder
        self.embed = EmbedBuilder(self)

        # initialize CommandChecks
        self.checks = CommandChecks(self)

        # get miscellaneous info
        self.admin_ids = set(self.config["BOT"]["ADMIN_IDS"])
        self.version = self.config["BOT"]["VERSION"]
        self.github = self.config["BOT"]["GITHUB_REPO_URL"]
        self.discord_invite = self.config["BOT"]["DISCORD_INVITE_URL"]
        self.documentation_url = self.config["BOT"]["DOCUMENTATION_URL"]
        self.invite_url = self.config["BOT"]["INVITE_URL"]
        self.default_prefix = self.config["BOT"]["DEFAULT_PREFIX"]
        self.default_language = self.config["BOT"]["DEFAULT_LANGUAGE"]
        self.development_server = discord.Object(id=self.config["BOT"]["DEVELOPMENT_SERVER_ID"])
        self.in_development = self.config["BOT"]["DEVELOPMENT_MODE"]

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
            chunk_guilds_at_startup=True,  # TODO: remove this and make it work wihout it
            max_messages=1000,
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree,
            owner_ids=self.admin_ids,
        )

    async def startup_hook(self):
        await self.load_extensions()
        print(self.startup_log)

    async def determine_prefix(self, bot_: commands.AutoShardedBot, message: discord.Message, /) -> List[str]:
        if guild := message.guild:
            prefix = await self.db.get(f"guilds.{guild.id}.prefix", default=self.default_prefix)
            return commands.when_mentioned_or(prefix)(bot_, message)
        return commands.when_mentioned_or(self.default_prefix)(bot_, message)

    async def load_extensions(self):
        loaded = []
        failed = {}
        for fn in map(
            lambda file_path: ".".join(file_path.paths)[:-3],
            pathlib.Path("./modules").glob(f"**/*.py"),
        ):
            try:
                await self.load_extension(fn)
                loaded.append(fn)
            except:  # noqa: 118
                failed[fn] = traceback.format_exc()
        log = []
        if loaded:
            log.append(color.green(listify(f"Successfully loaded {len(loaded)} modules", "\n".join(loaded))))
        for name, error in failed.items():
            log.append(color.red(listify(f"Failed to load {color.bold(name)}", error)))
        self.startup_log = "\n".join(log)

    def run(self):
        try:
            super().run(self.token, reconnect=True)
        finally:

            async def stop():
                await self.session.close()

            asyncio.run(stop())

    async def on_ready(self):
        self.uptime = math.floor(time.time())
        discord_info = listify("Discord Info", f"{color.bold('Version:')} {discord.__version__}")
        bot_info = listify(
            "Bot Info",
            f"{color.bold('User:')} {self.user}"
            f"\n{color.bold('ID:')} {self.user.id}"  # type: ignore
            f"\n{color.bold('Total Guilds:')} {len(self.guilds)}"
            f"\n{color.bold('Total Users:')} {len(self.users)}"
            f"\n{color.bold('Total Shards: ')} {self.shard_count}",
        )
        print(
            "\n\n".join(
                [color.cyan(discord_info), color.magenta(bot_info), color.yellow(f"Running on Clutter v{self.version}")]
            )
        )

    async def blacklist_user(self, user: Union[discord.User, discord.Member, int], /) -> bool:
        user_id = user if isinstance(user, int) else user.id
        if await self.db.get(f"users.{user_id}.blacklisted", default=False):
            return False
        await self.db.set(f"users.{user_id}.blacklisted", True)
        return True

    async def unblacklist_user(self, user: Union[discord.User, discord.Member, int], /) -> bool:
        user_id = user if isinstance(user, int) else user.id
        if not await self.db.get(f"users.{user_id}.blacklisted", default=False):
            return False
        await self.db.set(f"users.{user_id}.blacklisted", False)
        return True

    def add_command(self, command: commands.Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command is None:
            return

        if self.db.get(f"users.{ctx.author.id}.blacklisted", default=False):
            return

        if guild := ctx.guild:
            if self.db.get(f"guilds.{guild.id}.blacklisted", default=False):
                return

        if ctx.valid and getattr(ctx.cog, "qualified_name", None) != "Jishaku":
            await ctx.trigger_typing()
        await self.invoke(ctx)

    async def get_context(
        self, message: Union[discord.Message, discord.Interaction], /, *, cls: Optional[Type[ContextT]] = ClutterContext
    ) -> Union[ClutterContext, ContextT]:
        return await super().get_context(message, cls=cls)

    async def getch_member(self, guild: discord.Guild, user_id: int, /) -> Optional[discord.Member]:
        if member := guild.get_member(user_id) is not None:
            return member
        if self.get_shard(guild.shard_id).is_ws_ratelimited():
            try:
                return await guild.fetch_member(user_id)
            except discord.HTTPException:
                return None

        members = await guild.query_members(limit=1, user_ids=[user_id], cache=True)
        if not members:
            return None
        return members[0]


if __name__ == "__main__":
    bot = Clutter()
    bot.run()
