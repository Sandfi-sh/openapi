"""Set or verify an SDK's release version."""

import argparse
import json
import re
import subprocess
import tomllib
from pathlib import Path


def release(directory, version, check):
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Use a release version such as 0.1.1.")
    sdk_path = directory / "sdk.json"
    sdk = json.loads(sdk_path.read_text())
    if check:
        if sdk["version"] != version:
            raise ValueError("The tag and SDK versions differ.")
        generated = json.loads((directory / ".sdk-generated.json").read_text())
        if generated["sdk_version"] != version:
            raise ValueError("Regenerate the SDK for this release version.")
        if sdk["language"] == "python":
            actual = tomllib.loads((directory / "pyproject.toml").read_text())["project"]["version"]
        elif sdk["language"] == "typescript":
            actual = json.loads((directory / "package.json").read_text())["version"]
        else:
            actual = generated["sdk_version"]
        if actual != version:
            raise ValueError("The package and SDK versions differ.")
        print(f"Verified release version {version}.")
        return
    sdk["version"] = version
    sdk_path.write_text(json.dumps(sdk, indent=2) + "\n")
    if sdk["language"] == "python":
        path = directory / "pyproject.toml"
        path.write_text(re.sub(r'^version = "[^"]+"', f'version = "{version}"', path.read_text(), count=1, flags=re.M))
        subprocess.run(["uv", "lock"], cwd=directory, check=True)
    elif sdk["language"] == "typescript":
        subprocess.run(["npm", "version", version, "--no-git-tag-version", "--allow-same-version"], cwd=directory, check=True)
    print("Regenerate the SDK, run its checks, and commit the release candidate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--directory", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    release(args.directory.resolve(), args.version.removeprefix("v"), args.check)
