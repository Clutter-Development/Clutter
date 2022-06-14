import asyncio

import aiohttp
import discord
import time
import pathlib
from discord.ext import commands
from ..utils import color, db, embed, i18n

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent


class ClutterBot(commands.AutoShardedBot):
    invite_url: str
    start_time: float

    def __init__(self, config: dict, session: aiohttp.ClientSession, /) -> None:
        self.config = config
        self.session = session

        self.version = "0.0.2"

        self.support_invite = "https://discord.com/invite/mVKkMZRPQE"
        self.documentation_url = "https://clutter-development.github.io/"
        self.source_url = "https://github.com/Clutter-Development/Clutter"

        self.token = config["BOT_TOKEN"]

        self.default_language = config["BOT_DEFAULT_LANGUAGE"]
        self.default_prefix = config["BOT_DEFAULT_PREFIX"]

        # Auto spam control for commands.
        # Frequent triggering of this filter (3 times in a row) will result in a blacklist.
        self.spam_control = type("SpamControl", )
        mapping = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)
        self.spam_control.get_bucket = mapping.get_bucket
        self.spam_control.cooldown = mapping._cooldown

        self.embed = embed.EmbedCreator(config["STYLE"])

        self.db = db.CachedMongoManager(
            config["MONGO_URI"],
            database="clutter",
            max_items=5000
        )
        self.i18n = i18n.DiscordI18N(
            str(ROOT_DIR / "i18n"),
            db=self.db,
            fallback_language=self.default_language
        )

        self.error_webhook = discord.Webhook.from_url(
            config["ERROR_WEBHOOK_URL"], session=session
        )
        self.log_webhook = discord.Webhook.from_url(
            config["LOG_WEBHOOK_URL"], session=session
        )

        super().__init__(
            allowed_mentions=discord.AllowedMentions.none(),
            command_prefix=self.get_prefix,
            case_insensitive=True,
            intents=discord.Intents(
                guilds=True,
                members=True,
                messages=True,
                message_content=True,
            ),
            max_messages=1000,
            owner_ids=set(config["BOT_ADMIN_IDS"]),
            strip_after_prefix=True,
            tree_cls=ClutterCommandTree
        )

    # Sets the attributes that either need a user instance or needs to be set when the bot starts.

    async def setup_hook(self) -> None:
        self.start_time = time.time()

        self.invite_url = discord.utils.oauth_url(
            self.user.id, permissions=discord.Permissions(administrator=True)
        )

    # Gets the bot's uptime in seconds.

    @property
    def uptime(self) -> float:
        return time.time() - self.start_time

    # Adds global attributes to commands.

    async def add_command(self, command: commands.Command, /) -> None:
        command.cooldown_after_parsing = True
        super().add_command(command)

    # Triggers typing for commands.

    async def process_commands(self, message: discord.Message, /) -> None:
        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if not ctx.valid:
            return

        if (cog := ctx.cog) and cog.qualified_name != "Jishaku":
            await ctx.typing()

        await self.invoke(ctx)

    # Custom context.

    async def get_context(self, message: discord.Message, /) -> ClutterContext:
        return await super().get_context(message, cls=ClutterContext)

    # Start the bot.

    def run(self) -> None:
        async def runner() -> None:
            async with self:
                await self.load_extensions()
                await self.start(self.token)

        try:
            asyncio.run(runner())
        except KeyboardInterrupt:
            pass



