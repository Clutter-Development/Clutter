# Docs

(outdated, very)

## _class_ `MongoManager(connect_url: str, cooldown: int)`

Basic database manager.

* Parameters:
    * `connect_url`: The connection URL to the database.
    * `cooldown`: The time a value will be kept in the cache.
* Methods:
    * `refresh(path: Union[str, list])`: Refreshes the cache for the specified key(s).
    * `get(path: str, default: Any)`: Returns the cached data for the specified key. If the key is not found, returns
      the default value.
    * `set(path: str, value: Any)`: Sets the key value pair in the database.
    * `rem(path: str)`: Removes the key value pair from the database.
    * **Note:** The `path` parameter is seperated into `dbName.collectionName.documentName.varName` format, if it is
      longer than that, a nested dictionary will be created.
    * **Note:** The `refresh` method is called when calling the `get`\*, `set` and `rem` methods.
    * \* Only if the key is not cached, if it is, it calls the `_use_cache` method.
* Inner methods:
    * `_assemble_dict(path: str, value: Any)`: Assembles a nested dictionary from the key and value.
    * `_find_in_dict(get_from: dict, path: str)`: Finds the key value pair in the specified dictionary.
    * `_get_last_used(path: str)`: Returns the last time the key value pair was used.
    * `_use(path: str)`: Updates the last used time for the key value pair to now.
    * `_remove_after_cooldown(path: str)`: Removes the key value pair from the cache if the last used time is older than
      the cooldown time.
    * `_get_from_db(path: str)`: Returns the key value pair from the database.

## _class_ `Checks(db: MongoManager, bot: commands.Bot)`

A simple class for decorators that check if the user(or bot) has the required permissions.

Usage:

```python
from utils.init import checks
from discord.ext import commands
import discord


@commands.command(name="ban")
@commands.bot_has_permissions(send_messages=True, read_message_history=True, ban_members=True)
@commands.check_any(commands.is_owner(), checks.mod_only(), commands.has_permissions(ban_members=True))
async def _ban(self, ctx, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await ctx.reply(f"**{member} got bent**")
```

## _class_ `Chalk`

A simple class for printing colored text in the terminal.

* Methods:
    * `bold(text: str)`: Converts the text to bold.
    * `italic(text: str)`: Converts the text to italic.
    * `underline(text: str)`: Underlines the text.
    * `strike(text: str)`: Strikes through the text.
    * `blink(text: str)`: Blinks the text.
    * `black(text: str)`: Converts the text to black.
    * `red(text: str)`: Converts the text to red.
    * `green(text: str)`: Converts the text to green.
    * `yellow(text: str)`: Converts the text to yellow.
    * `blue(text: str)`: Converts the text to blue.
    * `magenta(text: str)`: Converts the text to magenta.
    * `cyan(text: str)`: Converts the text to cyan.
    * `white(text: str)`: Converts the text to white.
    * `black_bg(text: str)`: Converts the text background to black.
    * `red_bg(text: str)`: Converts the text background to red.
    * `green_bg(text: str)`: Converts the text background to green.
    * `yellow_bg(text: str)`: Converts the text background to yellow.
    * `blue_bg(text: str)`: Converts the text background to blue.
    * `magenta_bg(text: str)`: Converts the text background to magenta.
    * `cyan_bg(text: str)`: Converts the text background to cyan.
    * `white_bg(text: str)`: Converts the text background to white.
    * `black_hl(text: str)`: Converts the text highlight to black.
    * `red_hl(text: str)`: Converts the text highlight to red.
    * `green_hl(text: str)`: Converts the text highlight to green.
    * `yellow_hl(text: str)`: Converts the text highlight to yellow.
    * `blue_hl(text: str)`: Converts the text highlight to blue.
    * `magenta_hl(text: str)`: Converts the text highlight to magenta.
    * `cyan_hl(text: str)`: Converts the text highlight to cyan.
    * `white_hl(text: str)`: Converts the text highlight to white.