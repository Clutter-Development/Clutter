import os

from dotenv import load_dotenv

load_dotenv()

defaults = {  # im storing these locally because its faster
    "emojis": {
        "success": "<:success:889206855321157683>",
        "error": "<:error:911240678342819870>",
        "warning": "<:warning:889206830637666334>",
        "info": "<:info:889206906588106824>",
    },
    "colors": {"success": 0x34C789, "error": 0xFF005C, "warning": 0x006AFF, "info": 0x656479},
    "prefix": ">",
}

secrets = {
    "token": os.getenv("TOKEN"),
    "mongo_url": os.getenv("MONGO_URL"),
    "error_webhook": os.getenv("ERROR_WEBHOOK"),
}

bot_info = {
    "github": "https://github.com/Clutter-Development/Clutter",
    "discord": "",
    "invite": "",
    "owner_id": 512640455834337290,
    "bot_id": 884505093548949575,
    "version": "0.2b",
}
