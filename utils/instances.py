from config import mongo_url
from .content import ansi_color, embed_assembler, mongo_manager, checks
from ..main import bot

color = ansi_color.AnsiColor
db = mongo_manager.MongoManager(mongo_url, "Clutter")
embed = embed_assembler.EmbedAssembler(db)
checks = checks.Checks(db, bot)
