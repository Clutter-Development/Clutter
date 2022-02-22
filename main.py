import traceback

import discord
from discord.ext import commands

from config import secrets
from utils.init import chalk, embed, fancy_desc, get_all_py, get_prefix, get_txt

bot = commands.Bot(command_prefix=get_prefix, intents=discord.Intents().default(), help_command=None)

_modules_loaded, _modules_failed = "", ""
for fn, fp in get_all_py("./utils").items():
    try:
        bot.load_extension(fp)
    except Exception:
        _modules_failed += "\n" + fancy_desc(f"\nFailed to load {chalk.bold(fn)}", traceback.format_exc())
    else:
        _modules_loaded += f"{fn}\n"
start_log = f"{chalk.green(fancy_desc('Loaded', _modules_loaded[:-1]))}{chalk.red(_modules_failed)}"


@bot.event
async def on_ready():
    print(
        f"{start_log}\n{fancy_desc('Logged in as', bot.user.name)}\n{fancy_desc('Pycord version', discord.__version__)}\nConnected to {len(bot.guilds)} servers"
    )


@bot.command(name="load")
@commands.is_owner()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
async def _load(ctx, module: str):
    await ctx.channel.trigger_typing()
    modules = get_all_py("./modules")
    try:
        bot.load_extension(modules[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"**{module}** is not a valid module"), mention_author=False)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't load **{module}**"),
            file=get_txt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Loaded **{module}**"), mention_author=False)


@bot.command(name="reload")
@commands.is_owner()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
async def _reload(ctx, module: str):
    await ctx.channel.trigger_typing()
    modules = get_all_py("./modules")
    try:
        bot.reload_extension(modules[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"**{module}** is not a valid module"), mention_author=False)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't reload **{module}**"),
            file=get_txt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Reloaded **{module}**"), mention_author=False)


@bot.command(name="unload")
@commands.is_owner()
@commands.bot_has_permissions(send_messages=True, embed_links=True, read_message_history=True, attach_files=True)
async def _unload(ctx, module: str):
    await ctx.channel.trigger_typing()
    modules = get_all_py("./modules")
    try:
        bot.unload_extension(modules[module])
    except KeyError:
        await ctx.reply(embed=embed.error(ctx.guild.id, f"**{module}** is not a valid module"), mention_author=False)
    except Exception:
        await ctx.reply(
            embed=embed.error(ctx.guild.id, f"Couldn't unload **{module}**"),
            file=get_txt(traceback.format_exc(), "error"),
            mention_author=False,
        )
    else:
        await ctx.reply(embed=embed.success(ctx.guild.id, f"Unloaded **{module}**"), mention_author=False)


bot.run(secrets["token"])
