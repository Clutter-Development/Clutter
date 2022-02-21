import traceback

import discord
from discord.ext import commands

from utils.init import chalk, get_all_py, get_prefix, fancy_desc

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
