import asyncio
import math
import os
import sys
import time
import traceback
from glob import glob
from typing import List, Union

import aiohttp
import discord
import json5
from discord.ext import commands
from dotenv import load_dotenv
from utils import CachedMongoManager, CommandChecks, EmbedBuilder, color, listify
from core.slash_tree import ClutterCommandTree

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
        with open("./assets/colors.json5") as f:
            colors = json5.load(f)
        with open("./assets/emojis.json5") as f:
            emojis = json5.load(f)
        self.embed = EmbedBuilder(colors, emojis)

        # initialize CommandChecks
        self.checks = CommandChecks(self)

        # get miscellaneous info
        self.admin_ids = self.config["BOT"]["ADMIN_IDS"]
        self.invite_url = self.config["BOT"]["INVITE_URL"]
        self.default_prefix = self.config["BOT"]["DEFAULT_PREFIX"]
        self.default_language = self.config["BOT"]["DEFAULT_LANGUAGE"]
        self.development_server = discord.Object(id=self.config["BOT"]["DEVELOPMENT_SERVER_ID"])
        self.in_development = self.config["BOT"]["DEVELOPMENT_MODE"]

        with open("./misc.json5") as f:
            misc = json5.load(f)
        self.version = misc["BOT_VERSION"]
        self.github = misc["GITHUB_REPO_URL"]
        self.discord_invite = misc["DISCORD_INVITE_URL"]
        self.documentation_url = misc["DOCUMENTATION_URL"]

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
            chunk_guilds_at_startup=False,
            max_messages=1000,
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree,
        )

    async def startup_hook(self):
        await self.load_extensions()

    async def determine_prefix(self, bot_: commands.AutoShardedBot, message: discord.Message, /) -> List[str]:
        if guild := message.guild:
            prefix = await self.db.get(f"guilds{guild.id}.prefix", default=self.default_prefix)
            return commands.when_mentioned_or(prefix)(bot_, message)
        return commands.when_mentioned_or(self.default_prefix)(bot_, message)

    async def load_extensions(self):
        loaded = []
        failed = {}
        for fn in map(
            lambda file_path: file_path.replace(os.path.sep, ".")[:-3],
            glob(f"modules/**/*.py", recursive=True),
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
        print(self.startup_log)
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
        super().add_command(command)
        command.cooldown_after_parsing = True
        if not getattr(command._buckets, "_cooldown", None):  # noqa: 170
            command._buckets = commands.CooldownMapping.from_cooldown(1, 3, commands.BucketType.user)  # default cooldown is 1 per 3s

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.valid and getattr(ctx.cog, "qualified_name", None) != "Jishaku":
            await ctx.trigger_typing()
        await self.invoke(ctx)


if __name__ == "__main__":
    bot = Clutter()
    bot.run()
