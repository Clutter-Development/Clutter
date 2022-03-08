import traceback

import discord
from discord.ext import commands

from config import secrets
from utils.init import chalk, embed, listify, get_all_py, get_prefix, mktxt

intents = discord.Intents.default()
intents.members = True
# intents.message_content = True  On api v10
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

_modules_loaded, _modules_failed = "", ""
bot.load_extension("jishaku")
for fn, fp in get_all_py("./modules").items():
    try:
        bot.load_extension(fp)
    except Exception:
        _modules_failed += "\n" + listify(f"\nFailed to load {chalk.bold(fn)}", traceback.format_exc()[:-1])
    else:
        _modules_loaded += f"{fn}\n"
start_log = f"{chalk.green(listify('Loaded', _modules_loaded[:-1]))}{chalk.red(_modules_failed)}"


@bot.event
async def on_ready():
    print(
        f"{start_log}\n\n{listify('Logged in as', f'{bot.user.name}#{bot.user.discriminator}')}\n\n{listify('Pycord version', discord.__version__)}\n\nConnected to {len(bot.guilds)} servers"
    )


@bot.before_invoke
async def before_invoke(ctx):
    await ctx.trigger_typing()


@bot.command(name="load", aliases=["l"])
@commands.guild_only()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
@commands.is_owner()
async def _load(ctx, module: str):
    try:
        bot.load_extension(get_all_py("./modules")[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"'{module}' is not a valid module"), mention_author=False)
    except discord.ExtensionAlreadyLoaded:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"'{module}' is already loaded"), mention_author=False)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't load '{module}'"),
            file=mktxt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Loaded '{module}'"), mention_author=False)


@bot.command(name="reload", aliases=["rl"])
@commands.guild_only()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
@commands.is_owner()
async def _reload(ctx, module: str):
    try:
        bot.reload_extension(get_all_py("./modules")[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"'{module}' is not a valid module"), mention_author=False)
    except discord.ExtensionNotLoaded:
        await ctx.invoke(bot.get_command("load"), module)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't reload '{module}'"),
            file=mktxt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Reloaded '{module}'"), mention_author=False)


@bot.command(name="unload", aliases=["ul"])
@commands.guild_only()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
@commands.is_owner()
async def _unload(ctx, module: str):
    try:
        bot.unload_extension(get_all_py("./modules")[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"'{module}' is not a valid module"), mention_author=False)
    except discord.ExtensionNotLoaded:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"'{module}' is already unloaded"), mention_author=False)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't unload '{module}'"),
            file=mktxt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Unloaded '{module}'"), mention_author=False)


bot.run(secrets["token"])
