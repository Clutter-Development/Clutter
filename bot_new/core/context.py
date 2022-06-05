from discord.ext import commands


class ClutterContext(commands.Context):
    async def ok(self, value: bool, /) -> None:
        emojis = self.bot.config["STYLE"]["EMOJIS"]
        await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])
