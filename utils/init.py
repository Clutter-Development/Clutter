import json

from config import secrets
from utils.content import (
    chalk,
    checks,
    embed,
    fancy_desc,
    get_all_py,
    get_prefix,
    get_txt,
    mongodb,
    cmd
)

db = mongodb.MongoManager(secrets["mongo_url"], "Clutter", cooldown=4)

# Requires a database
checks = checks.Checks(db)  # To get the mod roles and user
embed = embed.Embed(db)  # To get the embed colors and emojis
get_prefix = get_prefix.get_prefix(db)  # To get the prefix

# Doesn't require a database
get_all_py = get_all_py.get_all_py
fancy_desc = fancy_desc.fancy_desc
chalk = chalk.Chalk
get_txt = get_txt.get_txt
with open("./utils/content/cmd.json", mode="r") as f:
    cmd = cmd.CommandsList(json.load(f))
