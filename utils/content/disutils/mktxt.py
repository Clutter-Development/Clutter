import os
import random
import string

import discord


def mktxt(text: str, filename: str) -> discord.File:
    fp = f"./temp/{''.join(random.choices(string.ascii_lowercase, k=10))}.txt"
    with open(fp, mode="w") as file:
        file.write(text)
    with open(fp, mode="rb") as file:
        file = discord.File(file, filename=f"{filename}.txt")
    os.remove(fp)
    return file
