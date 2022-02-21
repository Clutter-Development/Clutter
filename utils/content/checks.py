from discord.ext import commands


class Checks:
    def __init__(self, db):
        self.db = db

    def mod_only(self, **kwargs):
        async def predicate(ctx):
            return any(role.id in self.db.get(f"{ctx.guild.id}.moderators.roles") for role in
                       ctx.author.roles) or ctx.author.id in self.db.get(f"{ctx.guild.id}.moderators.users")

        return commands.check(predicate)

    # maybe add a check for bot maintainers?
    # will add if i need it later on
