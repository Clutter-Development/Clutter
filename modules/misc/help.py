from collections import defaultdict

from discord.ext import commands

from config import defaults
from utils.init import embed, db, cmd


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["imlost", "commands"])
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def help(self, ctx, command: str = ""):
        prefix = db.get(f'servers.{ctx.guild.id}.prefix', defaults['prefix'])[0]
        if command := cmd.get_command(command):
            _embed = embed.info(ctx.guild.id, f"Showing help for '{command.name}'", command.description)
            _embed.add_field(name="Usage", value=f"`{prefix}{command.usage}`")
            if aliases := command.aliases:
                _embed.add_field(name="Aliases", value=", ".join([f"`{alias}`" for alias in aliases]))
            if needs_perms := command.needs_perms:
                _embed.add_field(name="Needs Permissions", value=", ".join([f"`{perm}`" for perm in needs_perms]))
            _embed.add_field(name="Category", value=f"`{command.category}`")
            if parameters := command.parameters:
                _embed.add_field(name="Parameters", value="\n\n".join([
                                                                          f"**Name:** `{param.name}`\n**Type:** `{param.type}`\n**Required:** `{param.required}`\n**Description:** {param.description}"
                                                                          for param in parameters]))
        else:
            _embed = embed.info(ctx.guild.id, "Help",
                                f"Use `{prefix}help <command>` to get help for a specific command")
            res = defaultdict(list)
            for category, cmds in cmd.sort_by_category().items():
                for cmd_ in cmds:
                    res[category].append(f"`{cmd_.name}` - {cmd_.brief}")
            for category, description in res.items():
                _embed.add_field(name=category, value="\n".join(description))
        await ctx.reply(embed=_embed, mention_author=False)


def setup(bot):
    bot.add_cog(Help(bot))
