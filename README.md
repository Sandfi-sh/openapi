# Sandfish OpenAPI and SDK generation

This repository owns the public [Sandfish API](https://sandfi.sh/docs#api)
contract and reproducible generation of the Python, TypeScript, and Go SDKs.

## Source

`openapi.json` is exported from Sandfish's FastAPI definitions. `source.json`
records its revision and checksum. The deployed contract is available at
<https://sandfi.sh/docs/openapi.json>.

Only operations explicitly marked for SDK use enter this contract.
Administrator browser operations and internal services are excluded.

## Generate an SDK

Install Python 3.11 or later, Java 17 or later, and Go for Go formatting. Clone
this repository and the target SDK repository next to each other, then run:

```sh
python validate.py
python generate.py python --output ../sandfish-python
python generate.py typescript --output ../sandfish-typescript
python generate.py go --output ../sandfish-go
```

The script downloads OpenAPI Generator 7.26.0 and checks its pinned SHA-256.
It reads the SDK version from the target's `sdk.json`. It replaces generated
files recorded in `.sdk-generated.json` and preserves maintained helpers.
It normalizes line endings and trailing whitespace in generated source.

Verify reproducibility with `--check`:

```sh
python generate.py python --output ../sandfish-python --check
python check_sdk.py ../sandfish-python
```

`prepare.py` adds an equivalent single-value enum beside each `const` because
the pinned Go generator does not enforce `const`. It also gives the search
result union a stable model name. Nullable fields and discriminators retain
their original meaning. The Go configuration prefixes enum constants to avoid
collisions between status and domain types.

## Automatic updates

Install the prepared `.github/workflows` files to enable automatic updates.
The GitHub token used for installation must have the `workflow` scope.

Once installed, the contract workflow checks the deployed schema every six hours. It validates
the public-contract marker and opens a contract update PR when content changes.
It records the deployed revision from `X-Sandfish-Revision`.

Each SDK update workflow checks this repository every six hours. It regenerates source, runs
the SDK tests, and opens an update PR. Each workflow uses its own repository's
built-in Actions token, so updates do not depend on a personal token or a
cross-repository GitHub App. The updater explicitly starts CI for token-created
PRs. Enable **Allow GitHub Actions to create and approve pull requests** in each
repository's Actions settings; the workflows only create pull requests.

The complete update cycle is:

```text
API deployment → contract update PR → SDK update PRs → versioned releases
```

Use **Run workflow** to start synchronization before the next scheduled run.
The initial SDK contract can be a release candidate. `source.json` identifies
that state. The synchronizer waits until the public-contract export is deployed.

## Release

Read [RELEASING.md](RELEASING.md) for registry setup and the release procedure.
Review generated method and model changes before choosing a version. SDK
versions are independent of the API application's version.

Run `python -m unittest discover -s tests` for the contract-tool checks.

## License

The schema, generation scripts, SDKs, and examples use MIT. See [LICENSE](LICENSE).
