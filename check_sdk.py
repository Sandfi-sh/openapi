"""Run the checks required for one SDK repository."""

import argparse
import json
import subprocess
from pathlib import Path


def check(directory):
    language = json.loads((directory / "sdk.json").read_text())["language"]
    commands = {
        "python": [
            ["uv", "sync", "--locked", "--all-groups"],
            ["uv", "run", "ruff", "check", "."],
            ["uv", "run", "ruff", "format", "--check", "."],
            ["uv", "run", "pytest"],
            ["uv", "build"],
        ],
        "typescript": [["npm", "ci"], ["npm", "test"], ["npm", "pack", "--dry-run"]],
        "go": [["go", "test", "./..."], ["go", "vet", "./..."]],
    }
    for command in commands[language]:
        subprocess.run(command, cwd=directory, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    check(parser.parse_args().directory.resolve())
