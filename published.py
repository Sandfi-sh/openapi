"""Report whether an exact package version is already published."""

import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

parser = argparse.ArgumentParser()
parser.add_argument("language", choices=["python", "typescript"])
parser.add_argument("version")
parser.add_argument("--directory", type=Path, required=True)
args = parser.parse_args()
version = args.version.removeprefix("v")
urls = {
    "python": f"https://pypi.org/pypi/sandfish-sdk/{version}/json",
    "typescript": f"https://registry.npmjs.org/@sandfi-sh%2Fsdk/{version}",
}
try:
    with urlopen(urls[args.language], timeout=30) as response:
        published = json.load(response)
except HTTPError as exc:
    if exc.code != 404:
        raise
    print("exists=false")
else:
    if args.language == "python":
        remote = {item["filename"]: item["digests"]["sha256"] for item in published["urls"]}
        artifacts = [path for path in (args.directory / "dist").iterdir()
                     if path.name.startswith(f"sandfish_sdk-{version}-")
                     or path.name == f"sandfish_sdk-{version}.tar.gz"]
        if not artifacts:
            raise ValueError("Build the Python release before checking publication.")
        for artifact in artifacts:
            if remote.get(artifact.name) != hashlib.sha256(artifact.read_bytes()).hexdigest():
                raise ValueError("The published Python files differ from this release candidate.")
    else:
        with tempfile.TemporaryDirectory(prefix="sandfish-npm-check-") as temporary:
            subprocess.run(["npm", "pack", "--ignore-scripts", "--pack-destination", temporary],
                           cwd=args.directory, check=True, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            artifact = next(Path(temporary).glob("*.tgz"))
            integrity = "sha512-" + base64.b64encode(hashlib.sha512(artifact.read_bytes()).digest()).decode()
            if published["dist"].get("integrity") != integrity:
                raise ValueError("The published npm archive differs from this release candidate.")
    print("exists=true")
