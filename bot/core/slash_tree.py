import discord
from discord import app_commands as app


class ClutterCommandTree(app.CommandTree):
    def interaction_check(self, inter: discord.Interaction, /) -> bool:
        if self.client.in_development and inter.user.id not in self.client.admin_ids:
            await inter.response.defer(ephemeral=True, thinking=True)
            await inter.response.send_message(ephemeral=True, embed=self.client.embed.error("You can't use this command", "The bot is currently in development mode. Only bot admins can use this command."))
            return False
        elif self.client.db.get(f"users.{inter.user.id}.blacklisted", default=False):
            await inter.response.defer(ephemeral=True, thinking=True)
            await inter.response.send_message(ephemeral=True, embed=self.client.embed.error("You can't use this command", "You are blacklisted from the bot.\nIf you think this is a mistake, please a bot admin to unblacklist you."))
            return False
        return True


