import asyncio
import os
import random
import string

import discord


def get_txt(text: str, filename: str) -> discord.File:
    fn = f"./temp/{''.join(random.choices(string.ascii_lowercase, k=10))}.txt"
    with open(fn, mode="w") as file:
        file.write(text)
    with open(fn, mode="rb") as file:
        file = discord.File(file, filename=f"{filename}.txt")
    asyncio.create_task(delete_file_after(fn, 5))
    return file


async def delete_file_after(path: str, cooldown: int) -> None:
    await asyncio.sleep(cooldown)
    if os.path.exists(path):
        os.remove(path)
