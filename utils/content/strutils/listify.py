import re


def listify(title: str, description: str):
    newline = "\n"
    non_ansi = re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", title)
    return f"{title}:\n   ╭{(len(non_ansi.split(newline)[-1]) - 4) * '─'}╯\n{'   │' + f'{newline}   │'.join(description.split(newline))}"
