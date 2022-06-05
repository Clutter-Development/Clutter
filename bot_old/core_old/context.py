import discord
from discord.ext import commands


class ClutterContext(commands.Context):
    async def reply_embed(
            self,
            asset_type: str,
            title: str | None = None,
            /,
            description: str | None = None,
            *,
            mention: bool = False,
            view: discord.ui.View | None = None,
    ) -> discord.Message:

        """Replies an embed to the context.

        Args:
            asset_type (str): The embed asset type to reply with.
            title (str | None): The title of the embed.
            description (str | None, optional): The description of the embed. Defaults to None.
            mention (bool): Wheter or not to mention the author when replying. Defaults to False.
            view (discord.ui.View | None): The View to send with the message. Defaults to None

        Returns:
            discord.Message: The replied message.
        """
        return await self.reply(
            embed=self.bot.embed(asset_type, title, description=description),
            mention_author=mention,
            view=view,
        )

    async def ok(self, value: bool, /) -> None:
        """Reacts to the context message depending on the value.

        Args:
            value (bool): The value to react based on
        """
        emojis = self.bot.config["STYLE"]["EMOJIS"]
        await self.message.add_reaction(emojis["SUCCESS" if value else "ERROR"])

    async def maybe_dm_embed(
            self,
            asset_type: str,
            title: str | None = None,
            /,
            description: str | None = None,
    ) -> tuple[discord.Message | None, bool]:
        """DMs the author of the context an embed.

        Args:
            asset_type (str): The embed asset type to DM with.
            title (str | None): The title of the embed.
            description (str | None, optional): The description of the embed. Defaults to None.

        Returns:
            tuple[discord.Message | None, bool]: The DMed message and the success bool.
        """
        try:
            return (
                await self.author.send(
                    embed=self.bot.embed(asset_type, title, description=description)
                ),
                True,
            )
        except (discord.Forbidden, discord.HTTPException):
            return None, False
