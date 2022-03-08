import json

from config import secrets
from utils.content import (
    cmd,
    mongodb,
)
from utils.content.disutils import (
    checks,
    get_prefix,
    mktxt,
    embed
)
from utils.content.pathutils import get_all_py
from utils.content.strutils import (
    chalk,
    listify
)

db = mongodb.MongoManager(secrets["mongo_url"], "Clutter", cooldown=300)

# Requires a database
checks = checks.Checks(db)  # To get the mod roles and user
embed = embed.Embed(db)  # To get the embed colors and emojis
get_prefix = get_prefix.get_prefix(db)  # To get the prefix

# Doesn't require a database
get_all_py = get_all_py.get_all_py
listify = listify.listify
chalk = chalk.Chalk
mktxt = mktxt.mktxt
with open("./utils/content/cmd.json", mode="r") as f:
    cmd = cmd.CommandsList(json.load(f))
