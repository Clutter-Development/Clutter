import re

nonsi = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def fancy_desc(title: str, description: str):
    newline = "\n"
    non_ansi = nonsi.sub("", title)
    return f"{title}:\n   ╭{(len(non_ansi.split(newline)[-1]) - 4) * '─'}╯\n{'   │' + f'{newline}   │'.join(description.split(newline))}"