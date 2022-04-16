import logging
import os
import sys
from asyncio import run
from glob import glob
from math import floor
from time import time
from traceback import print_exception
from typing import List

import discord
from aiohttp import ClientSession
from discord import AllowedMentions, Intents, MemberCacheFlags, Message
from discord.ext.commands import AutoShardedBot, when_mentioned_or
from dotenv import load_dotenv
from json5 import load as load_json5
from rich.console import Console
from rich.logging import RichHandler
from utils import CachedMongoManager, ConfigError, EmbedBuilder

os.system("cls" if sys.platform == "win32" else "clear")


class Clutter(AutoShardedBot):
    def __init__(self):
        self.session = ClientSession()
        try:
            with open("config.json5") as f:
                config = load_json5(f)

            if config.get("USE_ENV", False):
                load_dotenv()
                self.token = os.getenv("BOT_TOKEN")
                webhook_url = os.getenv("ERROR_WEBHOOK")
                db_uri = os.getenv("MONGO_URI")
                if not all([self.token, webhook_url, db_uri]):
                    raise ConfigError("Missing required config variables in the .env file.")
            else:
                self.token = config["BOT"]["TOKEN"]
                webhook_url = config["LINKS"]["ERROR_WEBHOOK"]
                db_uri = config["DATABASE"]["URI"]

            self.webhook = discord.Webhook.from_url(webhook_url, session=self.session)
            self.db = CachedMongoManager(
                db_uri,
                database=config["DATABASE"]["NAME"],
                cooldown=config["DATABASE"]["CACHE_COOLDOWN"],
            )
            self.embed = EmbedBuilder(config["DEFAULTS"]["RESPONSES"], self.db)

            self.invite_url = config["BOT"]["INVITE_URL"]
            self.version = config["BOT"]["VERSION"]
            self.github = config["LINKS"]["GITHUB"]
            self.discord_invite = config["LINKS"]["DISCORD_INVITE"]
            self.documentation_url = config["LINKS"]["DOCUMENTATION"]

            self.development_server = discord.Object(id=config["DEVELOPMENT"]["SERVER_ID"])
            self.development_mode = discord.Object(id=config["DEVELOPMENT"]["DEVELOPMENT_MODE"])

            self.default_prefix = config["DEFAULTS"]["PREFIX"]

        except FileNotFoundError:
            raise ConfigError("config.json5 does not exist!")
        except ValueError:
            raise ConfigError("Invalid config.json5 file.")
        except KeyError as e:
            raise ConfigError(f"Missing required key and value pairs in config.json5: {e}")

        self.uptime: int

        logging.basicConfig(
            level=logging.INFO,
            format="[CLUTTER LOG] %(message)s",
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    omit_repeated_times=False,
                    show_path=False,
                    show_time=False,
                    markup=True,
                )
            ],
        )
        self.log = logging.getLogger("rich")
        self.console = Console(color_system="windows", force_terminal=True)

        intents = Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis_and_stickers=True,
            messages=True,
            reactions=True,
            message_content=True,
        )

        stuff_to_cache = MemberCacheFlags.from_intents(intents)
        allowed_mentions = AllowedMentions.none()
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

    async def determine_prefix(self, bot: AutoShardedBot, message: Message, /) -> List[str]:
        if guild := message.guild:
            prefix = await self.db.get(f"guilds{guild.id}.prefix", default=self.default_prefix)
            return when_mentioned_or(prefix)(bot, message)
        return when_mentioned_or(self.default_prefix)(bot, message)

    def load_extensions(self):
        loaded = []
        failed = []
        for fn in map(
            lambda file_path: file_path.replace(os.path.sep, ".")[:-3],
            glob(f"modules/**/*.py", recursive=True),
        ):
            try:
                self.load_extension(fn)
                loaded.append(fn)
                self.log.info(f"[bright_green][MODULE][/] Successfully loaded [bold]{fn}[/].")
            except Exception as e:
                failed.append(fn)
                self.log.error(f"[bright_red][MODULE][/] Failed to load [bold]{fn}[/]:")
                print_exception(type(e), e, e.__traceback__)
        return loaded, failed

    def run_bot(self):
        try:
            self.run(self.token, reconnect=True)
        finally:

            async def stop():
                await self.session.close()

            run(stop())

    async def on_ready(self):
        self.uptime = floor(time())  # noqa
        self.console.print(
            f"""[blue3]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Signed into Discord as [bold]{self.user}[/bold] [italic]({self.user.id})[/italic]
Discord.py version: [bold]{discord.__version__}[/bold]
Default prefix: [bold]{self.default_prefix}[/bold]
Development Mode: [bold]{"On" if self.development_mode else "Off"}[/bold]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        )


if __name__ == "__main__":
    bot = Clutter()
    bot.run_bot()
