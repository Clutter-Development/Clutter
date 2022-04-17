import os
import sys
import asyncio
from glob import glob
import math
import time
import traceback
from typing import List

import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
import json5
from utils import CachedMongoManager, EmbedBuilder, CommandChecks, listify, color

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
        self.development_mode = discord.Object(id=self.config["BOT"]["DEVELOPMENT_MODE"])

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
        )
        self.load_extensions()

    async def determine_prefix(self, bot: commands.AutoShardedBot, message: discord.Message, /) -> List[str]:
        if guild := message.guild:
            prefix = await self.db.get(f"guilds{guild.id}.prefix", default=self.default_prefix)
            return commands.when_mentioned_or(prefix)(bot, message)
        return commands.when_mentioned_or(self.default_prefix)(bot, message)

    def load_extensions(self):
        loaded = []
        failed = {}
        for fn in map(
            lambda file_path: file_path.replace(os.path.sep, ".")[:-3],
            glob(f"modules/**/*.py", recursive=True),
        ):
            try:
                self.load_extension(fn)
                loaded.append(fn)
            except:
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
        bot_info = listify("Bot Info", f"{color.bold('User:')} {self.user}"
                                       f"\n{color.bold('ID:')} {self.user.id}"
                                       f"\n{color.bold('Total Guilds:')} {len(self.guilds)}"
                                       f"\n{color.bold('Total Users:')} {len(self.users)}"
                                       f"\n{color.bold('Total Shards: ')} {self.shard_count}"
                           )
        print("\n\n".join([
            color.cyan(discord_info),
            color.magenta(bot_info),
            color.yellow(f"Running on Clutter v{self.version}")]
                         )
        )


if __name__ == "__main__":
    bot = Clutter()
    bot.run()
