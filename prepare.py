"""Apply equivalent schema annotations for the pinned SDK generator."""

from copy import deepcopy


def prepare(schema):
    document = deepcopy(schema)

    def visit(node):
        if isinstance(node, list):
            for item in node:
                visit(item)
        elif isinstance(node, dict):
            # Some generators ignore const. A single-value enum has the same meaning.
            if "const" in node:
                node["enum"] = [node["const"]]
            for value in node.values():
                visit(value)

    visit(document)
    search = document["components"]["schemas"]["SearchResponse"]
    search["properties"]["items"]["items"]["title"] = "SearchResult"
    return document
