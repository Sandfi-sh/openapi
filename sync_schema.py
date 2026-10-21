"""Fetch the deployed public contract and record its source identity."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

from validate import validate

ROOT = Path(__file__).resolve().parent
URL = "https://sandfi.sh/docs/openapi.json"


def synchronize():
    with urlopen(Request(URL, headers={"User-Agent": "Sandfish-SDK-sync"}), timeout=60) as response:
        schema = json.load(response)
        revision = response.headers.get("X-Sandfish-Revision", "unknown")
    if schema.get("x-sandfish-sdk-contract") != 1:
        print("The deployed SDK contract is not available yet.")
        return
    validate(schema)
    content = (json.dumps(schema, indent=2, sort_keys=True) + "\n").encode()
    destination = ROOT / "openapi.json"
    if destination.exists() and destination.read_bytes() == content:
        print("The deployed contract is unchanged.")
        return
    destination.write_bytes(content)
    metadata = {
        "source_url": URL,
        "source_revision": revision,
        "schema_sha256": hashlib.sha256(content).hexdigest(),
        "status": "deployed",
    }
    (ROOT / "source.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(f"Imported the deployed contract from revision {revision}.")


if __name__ == "__main__":
    synchronize()
