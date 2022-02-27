import json

from discord.ext import commands

from config import defaults
from utils.init import embed, db


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open("./modules/misc/commands.json", "r") as f:
            self.commands = json.load(f)

    @commands.command(name="help")
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def help(self, ctx, command: str = None):
        prefix = db.get(f'servers.{ctx.guild.id}.prefix', defaults['prefix'])[0]
        all_commands = {}
        for v in self.commands.values():
            for k_, v_ in v.items():
                all_commands[k_] = v_
        if command in all_commands:
            _embed = embed.info(ctx.guild.id, f"Showing Help for **{command}**", all_commands[command]["desc"])
            _embed.add_field(name="Usage", value=f"`{prefix}{all_commands[command]['usage']}`", inline=False)
        else:
            _embed = embed.info(ctx.guild.id, "Showing help for all commands",
                                f"Use `{prefix}help <command>` to see more info about a command")
            for section, values in self.commands.items():
                _embed.add_field(name=section,
                                 value="\n".join([f"`{prefix}{v['usage']}` - {v['brief']}" for v in values.values()]),
                                 inline=False)
        _embed.set_footer(text="<> = required, [] = optional")
        await ctx.send(embed=_embed, mention_author=False)


def setup(bot):
    bot.add_cog(Help(bot))
