import discord
from discord import app_commands as app
from utils import GuildIsBlacklisted, InDevelopmentMode, UserIsBlacklisted


class ClutterCommandTree(app.CommandTree):
    def interaction_check(self, inter: discord.Interaction, /) -> bool:
        user_id = inter.user.id

        if self.client.in_development and not self.client.is_owner(inter.user):
            raise InDevelopmentMode("This bot is currently in development mode. Only bot admins can use commands.")

        if self.client.db.get(f"users.{user_id}.blacklisted", default=False):
            raise UserIsBlacklisted(f"You are blacklisted from using the bot.")

        if guild_id := inter.guild_id:
            if self.client.db.get(f"guilds.{guild_id}.blacklisted", default=False):
                raise GuildIsBlacklisted(f"This guild is blacklisted from using the bot.")

        return True
