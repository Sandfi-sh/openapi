"""Generate managed SDK files from the committed public contract."""

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from urllib.request import urlopen

from prepare import prepare
from validate import validate

ROOT = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalize_files(files):
    """Use LF endings and remove generated trailing whitespace."""
    result = {}
    for name, data in files.items():
        content = b"\n".join(line.rstrip(b"\r \t") for line in data.split(b"\n")).rstrip(b"\n")
        result[name] = content + b"\n" if content else b""
    return result


def generator_jar(settings, supplied=None):
    path = supplied or ROOT / ".cache" / f"openapi-generator-cli-{settings['version']}.jar"
    if not path.exists():
        version = settings["version"]
        url = ("https://repo.maven.apache.org/maven2/org/openapitools/openapi-generator-cli/"
               f"{version}/openapi-generator-cli-{version}.jar")
        with urlopen(url, timeout=120) as response:
            data = response.read()
        if digest(data) != settings["sha256"]:
            raise ValueError("The generator download failed checksum verification.")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if digest(path.read_bytes()) != settings["sha256"]:
        raise ValueError("The generator JAR does not match the pinned checksum.")
    return path


def managed_files(directory, language):
    if language == "python":
        return {str(p.relative_to(directory)): p.read_bytes()
                for p in (directory / "src/sandfish_sdk/generated").rglob("*.py")}
    if language == "typescript":
        source = directory / "src" if (directory / "src").exists() else directory
        return {str(Path("src/generated") / p.relative_to(source)): p.read_bytes()
                for p in source.rglob("*.ts")}
    return {p.name: p.read_bytes() for p in directory.glob("*.go")} | {
        "go.mod": (directory / "go.mod").read_bytes(),
        "go.sum": (directory / "go.sum").read_bytes(),
    }


def generate(language, output, jar=None, check=False):
    settings = json.loads((ROOT / "generator.json").read_text())
    schema_bytes = (ROOT / "openapi.json").read_bytes()
    schema = json.loads(schema_bytes)
    validate(schema)
    config = json.loads((ROOT / "configs" / f"{language}.json").read_text())
    sdk = json.loads((output / "sdk.json").read_text())
    version = sdk["version"]
    config["npmVersion" if language == "typescript" else "packageVersion"] = version
    jar = generator_jar(settings, jar)
    with tempfile.TemporaryDirectory(prefix="sandfish-codegen-") as temporary:
        temporary = Path(temporary)
        (temporary / "input.json").write_text(json.dumps(prepare(schema), sort_keys=True))
        (temporary / "config.json").write_text(json.dumps(config, sort_keys=True))
        command = ["java", "-Xmx2g", "-jar", str(jar), "generate",
                   "-i", str(temporary / "input.json"), "-g", settings["targets"][language],
                   "-c", str(temporary / "config.json"), "-o", str(temporary / "output"),
                   "--global-property", "apiTests=false,modelTests=false,apiDocs=false,modelDocs=false"]
        subprocess.run(command, check=True, timeout=1800)
        generated = temporary / "output"
        if language == "go":
            subprocess.run(["gofmt", "-w", *map(str, generated.glob("*.go"))], check=True)
        files = normalize_files(managed_files(generated, language))
    if not files:
        raise ValueError("The generator produced no source files.")
    previous_path = output / ".sdk-generated.json"
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {"files": {}}
    metadata = {
        "format_version": 1,
        "schema_sha256": digest(schema_bytes),
        "generator_version": settings["version"],
        "generator_sha256": settings["sha256"],
        "config_sha256": digest(json.dumps(config, sort_keys=True).encode()),
        "prepare_sha256": digest((ROOT / "prepare.py").read_bytes()),
        "sdk_version": version,
        "files": {path: digest(data) for path, data in sorted(files.items())},
    }
    files[".sdk-generated.json"] = (json.dumps(metadata, indent=2, sort_keys=True) + "\n").encode()
    stale = set(previous["files"]) - set(files)
    if language == "python":
        stale = {path for path in stale if path.startswith("src/sandfish_sdk/generated/")}
    if check:
        changed = [path for path, data in files.items()
                   if not (output / path).exists() or (output / path).read_bytes() != data]
        if changed or any((output / path).exists() for path in stale):
            raise SystemExit("Generated SDK files are stale. Run the generation command.")
        print(f"Verified reproducible {language} generation.")
        return
    for path in stale:
        destination = (output / path).resolve()
        if not destination.is_relative_to(output.resolve()):
            raise ValueError("Invalid managed file path.")
        destination.unlink(missing_ok=True)
    for path, data in files.items():
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print(f"Generated {language} SDK {version}: {len(files) - 1} files.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("language", choices=["python", "typescript", "go"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--jar", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generate(args.language, args.output.resolve(), args.jar, args.check)
