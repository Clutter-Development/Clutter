from re import sub

__all__ = ("format_as_list",)


def format_as_list(title: str, description: str, /, *, indent: int = 4) -> str:
    """Makes a fancy list(ish) thing out of a title and description. You can call this black magic fuckery.

    Args:
        title (str): The title of the list.
        description (str): The description of the list.
        indent (int): The indent size.

    Returns:
        str: The listified string.

    Example:
        Title Here:
           ╭──────╯
           │Description
           │Stuff
           │Etc
    """

    def create_line(length: int, inverted: bool, /):
        length -= 2
        corners = ("╭", "╯") if inverted else ("╰", "╮")
        return corners[0] + length * "─" + corners[1]

    title_len = len(
        sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", title)
    ) + int(bool(indent))
    lines = [f"{title}:"]

    if title_len > indent:
        lines.append(
            (indent - 1) * " "
            + create_line(
                title_len - indent + int(bool(indent or title_len)), True
            )
        )
    elif indent > title_len:
        lines.append(
            (title_len - 1) * " " + create_line(indent - title_len + 1, False)
        )

    lines.extend(
        f"{(indent - 1) * ' '}│{line}" for line in description.splitlines()
    )

    return "\n".join(lines)
