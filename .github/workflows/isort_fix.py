from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent / "clutter"

for fp in ROOT_DIR.rglob("*.py"):
    if fp.parts[-1] != "__init__.py" or not (content := fp.read_text()):
        continue

    old_c = content[:]

    while content[0] == "\n":
        content = content[1:]

    if old_c != (
        new := content.removeprefix("from __future__ import annotations")
    ):
        while new[0] == "\n":
            new = new[1:]

        fp.write_text(new)
