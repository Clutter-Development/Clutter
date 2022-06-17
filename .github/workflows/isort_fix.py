rom pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent / "clutter"

for fp in ROOT_DIR.rglob("*.py"):
    if fp.parts[-1] == "__init__.py" and (content := fp.read_text()) != (
        new := content.removeprefix("from __future__ import annotations")
    ):
        fp.write_text(new)
