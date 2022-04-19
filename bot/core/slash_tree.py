import discord
from discord import app_commands as app
from utils import UserBlacklisted, GuildBlacklisted, InDevelopmentMode


class ClutterCommandTree(app.CommandTree):
    def interaction_check(self, inter: discord.Interaction, /) -> bool:
        user_id = inter.user.id
        if self.client.in_development and not self.client.is_owner(inter.user):
            raise InDevelopmentMode("The bot is currently in development mode.")
        elif self.client.db.get(f"users.{user_id}.blacklisted", default=False):
            raise UserBlacklisted(f"You are blacklisted from using the bot.")
        elif guild_id := inter.guild_id:
            if self.client.db.get(f"guilds.{guild_id}.blacklisted", default=False):
                raise GuildBlacklisted(f"This guild is blacklisted from using the bot.")
        return True
