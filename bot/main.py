import os

import aiohttp
import discord
import json5
from discord.ext import commands
from dotenv import load_dotenv

from utils import CachedMongoManager, ConfigError


class Clutter(commands.AutoShardedBot):
    def __init__(self):
        self.session = aiohttp.ClientSession()
        try:
            with open("config.json5") as f:
                config = json5.load(f)

            if config.get("use_env_for_critical", False):
                load_dotenv()
                self.token = os.getenv("BOT_TOKEN")
                self.error_webhook = discord.Webhook.from_url(os.getenv("ERROR_WEBHOOK"), session=self.session)
                self.db = CachedMongoManager(
                    os.getenv("MONGO_URI"),
                    database=config["database"]["database_name"],
                    cooldown=config["database"]["cache_cooldown"]
                )
            else:
                self.token = config["bot"]["token"]
                self.error_webhook = discord.Webhook.from_url(config["links"]["error_webhook_url"],
                                                              session=self.session)

            self.invite_url = config["bot"]["invite_url"]
            self.version = config["bot"]["version"]
            self.github = config["links"]["github_repo_url"]
            self.discord_invite = config["links"]["discord_invite_url"]
            self.documentation_url = config["links"]["documentation_url"]

            self.development_server = discord.Object(id=config["development"]["server_id"])
            self.development_mode = discord.Object(id=config["development"]["development_mode"])

            self.default_prefix = config["defaults"]["prefix"]

        except (ValueError, FileNotFoundError, KeyError) as e:
            raise ConfigError(e)
