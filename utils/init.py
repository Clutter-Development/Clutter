from config import secrets
from content import chalk, checks, embed, get_prefix, get_txt, mod_event, mongodb

db = mongodb.MongoManager(secrets["mongo_url"], 1800)

# Requires a database
checks = checks.Checks(db)  # To get the mod roles and user
embed = embed.Embed(db)  # To get the embed colors and emojis
get_prefix = get_prefix.get_prefix(db)  # To get the prefix

# Doesn't require a database
chalk = chalk.Chalk
get_txt = get_txt.get_txt
ModEvent = mod_event.ModEvent
