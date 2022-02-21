import discord


class ModEvent:
    """
    Usage:
        event = ModEvent(mod=ctx.author, target=member, reason=reason, action="ban", guild_id=ctx.guild.id)
        self.bot.dispatch("modlog", event)
    """

    def __init__(self, *, mod: discord.Member, target: discord.Member, action: str, guild_id: int, reason: str = None,
                 ends_at: int = None, automod: bool = False):
        self.mod = mod
        self.target = target
        self.action = action
        self.guild_id = guild_id
        self.reason = reason or None
        self.ends_at = ends_at or None
        self.automod = automod
