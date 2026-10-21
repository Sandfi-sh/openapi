"""Validate the public contract before generation or synchronization."""

import argparse
import json
from pathlib import Path


def validate(schema):
    if schema.get("x-sandfish-sdk-contract") != 1:
        raise ValueError("The source is not a supported Sandfish SDK contract.")
    if schema.get("openapi") != "3.1.0":
        raise ValueError("The OpenAPI version needs a generator compatibility check.")
    if schema.get("servers") != [{"url": "https://sandfi.sh"}]:
        raise ValueError("The contract has an unexpected server URL.")
    operations = set()
    for path, item in schema["paths"].items():
        if not path.startswith("/api/") or path.startswith(("/api/admin/", "/api/sitemaps/")):
            raise ValueError(f"Unsupported SDK path: {path}")
        for method, operation in item.items():
            if method not in {"get", "post", "patch", "put", "delete", "head", "options"}:
                raise ValueError(f"Unsupported path item: {method}")
            name = operation["operationId"]
            if name in operations or operation.get("x-sdk-supported") is not True:
                raise ValueError(f"Invalid SDK operation: {name}")
            operations.add(name)
            for code in ("422", "429", "default"):
                ref = operation["responses"][code]["content"]["application/json"]["schema"]
                if ref != {"$ref": "#/components/schemas/ErrorResponse"}:
                    raise ValueError(f"Unexpected error response: {name} {code}")

    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            if "$ref" in node:
                ref = node["$ref"]
                if not ref.startswith("#/"):
                    raise ValueError("External schema references are not supported.")
                target = schema
                for part in ref[2:].split("/"):
                    target = target[part.replace("~1", "/").replace("~0", "~")]
            for value in node.values():
                visit(value)

    visit(schema)
    return len(operations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("schema", nargs="?", type=Path, default=Path(__file__).with_name("openapi.json"))
    args = parser.parse_args()
    count = validate(json.loads(args.schema.read_text()))
    print(f"Validated {count} SDK operations.")
