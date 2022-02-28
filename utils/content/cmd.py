from collections import defaultdict
from typing import Optional


class Parameter:

    def __init__(self, raw: dict):
        self.name = raw["name"]
        self.description = raw["description"]
        self.type = raw["type"]
        self.required = raw["required"]


class Command:

    def __init__(self, raw: dict):
        self.name = raw["name"]
        self.category = raw["category"]
        self.brief = raw["brief"]
        self.description = raw["description"]
        self.needs_perms = raw["needs_perms"]
        self.aliases = raw["aliases"]
        self.parameters = [Parameter(p) for p in raw["parameters"]]
        self.usables = [*self.aliases, self.name]

    @property
    def usage(self) -> str:
        return f"{self.name} {' '.join([f'<{p.name}>' if p.required else f'[{p.name}]' for p in self.parameters])}"


class CommandsList:

    def __init__(self, raw: list):
        self.raw = raw

    def get_command(self, name: str) -> Optional[Command]:
        for cmd in self.raw:
            cmd = Command(cmd)
            if name in cmd.usables:
                return cmd
        return None

    def sort_by_category(self) -> dict:
        res = defaultdict(list)
        for cmd in self.raw:
            cmd = Command(cmd)
            res[cmd.category].append(cmd)
        return dict(res)
