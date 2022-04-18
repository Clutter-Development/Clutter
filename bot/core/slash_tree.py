import discord
from discord import app_commands as app
from utils import NotAnAdmin, Blacklisted


class ClutterCommandTree(app.CommandTree):
    def interaction_check(self, inter: discord.Interaction, /) -> bool:
        if self.client.in_development and inter.user.id not in self.client.admin_ids:
            raise NotAnAdmin("User is not a bot admin.")
        elif self.client.db.get(f"users.{inter.user.id}.blacklisted", default=False):
            raise Blacklisted("User is blacklisted.")
        return True
