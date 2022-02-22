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
)

db = mongodb.MongoManager(secrets["mongo_url"], "Clutter", cooldown=1800)

# Requires a database
checks = checks.Checks(db)  # To get the mod roles and user
embed = embed.Embed(db)  # To get the embed colors and emojis
get_prefix = get_prefix.get_prefix(db)  # To get the prefix

# Doesn't require a database
get_all_py = get_all_py.get_all_py
fancy_desc = fancy_desc.fancy_desc
chalk = chalk.Chalk
get_txt = get_txt.get_txt
