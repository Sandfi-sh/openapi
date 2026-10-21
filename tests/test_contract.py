import copy
import json
import unittest
import tempfile
from pathlib import Path

from generate import managed_files, normalize_files
from prepare import prepare
from validate import validate

ROOT = Path(__file__).resolve().parents[1]


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / "openapi.json").read_text())

    def test_current_contract(self):
        self.assertGreater(validate(self.schema), 100)

    def test_const_annotations_keep_the_same_value(self):
        before = copy.deepcopy(self.schema)
        prepared = prepare(self.schema)
        discriminator = prepared["components"]["schemas"]["GroupSearchResult"]["properties"]["type"]
        self.assertEqual(discriminator["enum"], [discriminator["const"]])
        self.assertEqual(self.schema, before)

    def test_old_full_schema_is_rejected(self):
        self.schema.pop("x-sandfish-sdk-contract")
        with self.assertRaises(ValueError):
            validate(self.schema)

    def test_an_unapproved_operation_is_rejected(self):
        self.schema["paths"]["/api/analyses"]["get"]["x-sdk-supported"] = False
        with self.assertRaises(ValueError):
            validate(self.schema)

    def test_external_reference_is_rejected(self):
        self.schema["components"]["schemas"]["SubmitUrlRequest"]["properties"]["url"] = {"$ref": "https://example.com/schema.json"}
        with self.assertRaises(ValueError):
            validate(self.schema)

    def test_python_generation_preserves_the_maintained_package(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generated = root / "src/sandfish_sdk/generated"
            generated.mkdir(parents=True)
            (generated / "api_client.py").write_text("# Generated client\n")
            (generated.parent / "__init__.py").write_text("# Maintained package\n")
            files = managed_files(root, "python")
            self.assertIn("src/sandfish_sdk/generated/api_client.py", files)
            self.assertNotIn("src/sandfish_sdk/__init__.py", files)

    def test_source_format_is_stable_across_line_endings(self):
        self.assertEqual(normalize_files({"file.py": b"x = 'value ' \r\n\r\n"}),
                         {"file.py": b"x = 'value '\n"})


if __name__ == "__main__":
    unittest.main()
