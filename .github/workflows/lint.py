from __future__ import annotations

from pathlib import Path
from re import match

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

for fp in ROOT_DIR.rglob("*"):
    if not fp.is_file() or not (content := fp.read_text()):
        continue

    old_content = content[:]

    while content[0] == "\n":
        content = content[1:]

    if str(fp) == "__init__.py":
        content = content.removeprefix("from __future__ import annotations")

    if not content.endswith("\n"):
        content += f"{content}\n"

    while content[0] == "\n":
        content = content[1:]

    if old_content != content:

        fp.write_text(content)
