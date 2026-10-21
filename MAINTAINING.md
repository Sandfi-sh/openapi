# Maintain the Sandfish SDKs

[Generation guide](README.md) · [Release guide](RELEASING.md)

## Start with the requested result

Identify the user action and expected result. For example, a new endpoint must
be callable from the affected SDKs. A release must install from its registry
and complete an API call.

Check each affected repository before editing:

```sh
git status --short --branch
git fetch origin
git log --oneline origin/main..HEAD
```

Use the repository's actual tracking branch if it differs from `main`.
Preserve local changes and unpublished commits. Check remote files and Actions
runs before describing automation as active. Local workflow files do not prove
that GitHub has received them.

The [initial release record](docs/INITIAL_RELEASE_2026_10_21.md) records the
first verified releases and unfinished setup. Recheck that dated state before
resuming it. Temporary tool downloads and old access tokens are not required
parts of this project.

## Repositories and ownership

The canonical GitHub owner is `Sandfi-sh`. Lowercase repository URLs resolve,
but use the exact owner in case-sensitive trusted publisher settings.

| Repository | Change here |
|---|---|
| Sandfish application | FastAPI routes, Pydantic models, public operation selection, and deployed schema |
| [openapi](https://github.com/Sandfi-sh/openapi) | Contract import, generator configuration, schema preparation, and shared update tools |
| [sandfish-python](https://github.com/Sandfi-sh/sandfish-python) | Python helpers, package metadata, and Python tests |
| [sandfish-typescript](https://github.com/Sandfi-sh/sandfish-typescript) | TypeScript helpers, JavaScript modules, declarations, and npm metadata |
| [sandfish-go](https://github.com/Sandfi-sh/sandfish-go) | Go helpers, module metadata, and Go tests |
| [examples](https://github.com/Sandfi-sh/examples) | Consumer examples and their dependency versions |
| [.github](https://github.com/Sandfi-sh/.github) | Organization profile, shared contribution guidance, and issue templates |
| [azizollah1983](https://github.com/azizollah1983/azizollah1983) | Personal GitHub profile |

The SDK repositories are independent Git repositories. Clone `openapi` and
the language repositories beside each other for the documented commands.
Read `docs/SDKS.md` in the application checkout for application-side changes.

| Language | Registry identity | Import identity |
|---|---|---|
| Python | PyPI `sandfish-sdk` | `sandfish_sdk` |
| TypeScript and JavaScript | npm `@sandfi-sh/sdk` | `@sandfi-sh/sdk` |
| Go | Git tags | `github.com/sandfi-sh/sandfish-go` |

The PyPI project `sandfish` is unrelated. GitHub ownership does not reserve a
PyPI name or grant access to an npm scope. The npm `sandfi-sh` account owns the
scope used for the initial release. A separate npm organization is not needed.
The public SDKs, contract tools, and examples use the MIT license.

## Choose the correct change path

### API contract change

1. Change the route or model in the application repository.
2. Update its public operation selection and contract tests.
3. Follow the application's export and full-check procedure.
4. Import the public export into this repository with accurate provenance.
5. Generate and test each affected SDK.
6. Review compatibility before choosing release versions.
7. Update affected consumer examples.

The application exports a full frontend schema and a public SDK schema.
Import only `sandfish_web/openapi.public.json` for SDK generation. The public
export has `x-sandfish-sdk-contract: 1`. Administrator, internal-service,
sitemap, and rule-control operations are outside this contract.

The SDK server URL is `https://sandfi.sh`. Operation paths already include
`/api`. Do not append `/api` to the server URL. The full frontend schema must
remain suitable for the application's configured API origin.

Operation IDs determine generated method names. Review required fields,
nullable fields, discriminators, authentication, scopes, errors, uploads, and
download media types when changing an operation. Schema metadata does not
change runtime authorization.

### Client helper change

Change the maintained helper and its behavior tests in the language repository.
Use the generated methods for endpoint calls. Preserve the documented polling,
retry, cancellation, error, and streaming behavior.

Submissions are sent once. Read retries apply to GET and HEAD responses with
HTTP 429, 502, 503, or 504. A successful operation is separate from a verdict.
An evaluation can be null while work is in progress.

### Generator change

Use [generator.json](generator.json), [configs](configs),
[prepare.py](prepare.py), and [generate.py](generate.py). The generator is free
to run locally and does not require a paid generation service.

`generate.py` reads the target version from `sdk.json`. It downloads the pinned
JAR, verifies its SHA-256, generates in a temporary directory, and copies only
managed files. `--jar` can reuse a downloaded JAR with the same checksum.
Run `--check` after generation to verify repeatable output.

`.sdk-generated.json` records the schema, generator, effective configuration,
schema-preparation hashes, SDK version, and generated file hashes. Preserve
that file. It defines which old generated files the tool can remove.

| Language | Generated files | Maintained files |
|---|---|---|
| Python | `src/sandfish_sdk/generated/` | `src/sandfish_sdk/__init__.py`, `client.py`, `py.typed`, package metadata, and tests |
| TypeScript | `src/generated/` | `src/client.ts`, `src/index.ts`, package metadata, and tests |
| Go | Files listed in `.sdk-generated.json`, including `go.mod` and `go.sum` | `helpers.go`, `helpers_test.go`, `sdk.json`, and documentation |

Keep these generator compatibility corrections:

- Python's generated files must stay below `src/sandfish_sdk/generated`.
  Copying the generated parent initializer can remove the maintained exports.
- Python exposes async methods and typed `_sync` variants. Use one mode per
  client instance and close it through the corresponding context manager.
- Go needs `enumClassPrefix` to prevent constants with the same name in
  different model types from causing compile errors.
- `prepare.py` adds an equivalent single-value enum beside `const`. The pinned
  Go generator needs that annotation for search-result discrimination.
- The search-result union has the stable name `SearchResult`.
- Generated source uses LF endings and has no trailing whitespace. Go output
  also passes through `gofmt`.

Test all three SDKs after a shared generator or schema-preparation change.
Do not patch generated files to hide a generator defect. Fix the owning input
or preparation step, then regenerate.

## Contract provenance and deployment

[source.json](source.json) describes the source of `openapi.json`.
`candidate` means that the contract came from a source revision whose deployed
public export has not been verified. Package publication does not establish
application deployment.

After an authorized application deployment, inspect:

- `https://sandfi.sh/docs/openapi.json` and its contract marker.
- The `X-Sandfish-Revision` response header.
- The schema content compared with the checked export.

Run `python sync_schema.py` from this repository to import the deployed
contract. It validates the marker and schema before replacing the local copy.

**Current limit:** [sync_schema.py](sync_schema.py) returns before updating
`source.json` when the schema bytes are unchanged. Thus, a deployed candidate
can retain `status: candidate`. After verifying the header and schema, update
the provenance explicitly. A future metadata-only synchronization improvement
must test this case. Do not report an unknown revision as a verified release.

## Activate and maintain Actions

The workflow files define this sequence:

| Repository and workflow | Role |
|---|---|
| `openapi`: `ci.yml` | Validate the contract and generate and test all three SDKs |
| `openapi`: `sync.yml` | Check the deployed contract every six hours and propose changes |
| `openapi`: `update-sdk.yml` | Shared workflow for generating and testing one SDK update |
| Each SDK: `ci.yml` | Run language checks |
| Each SDK: `update.yml` | Call the shared update workflow every six hours |
| Each SDK: `release.yml` | Publish a version tag after language checks |

The update workflows use each repository's built-in `GITHUB_TOKEN`. They do
not require a cross-repository GitHub App or a stored personal token.
`contents: write`, `pull-requests: write`, and `actions: write` support update
branches, PR creation, and explicit CI dispatch.

GitHub does not start ordinary PR workflows for PRs created with that token.
[propose.py](propose.py) explicitly dispatches `ci.yml` on the update branch.
It stages the current directory, so run it only in an isolated task checkout.
The workflow checks the candidate before calling it.

To activate the prepared setup:

1. Check the remote workflow files and the unpublished local commits.
2. Use GitHub credentials that can write workflow files. A classic token needs
   the `workflow` scope in addition to repository access.
3. Enable **Allow GitHub Actions to create and approve pull requests** at the
   organization and repository levels. An organization restriction caused
   HTTP 409 when only the repository setting was changed during initial setup.
4. Publish `openapi` workflows before the SDK workflows that call them.
5. Run the contract CI and each language CI. Inspect the resulting run IDs.
6. Dispatch the contract sync and SDK update workflows. Confirm an unchanged
   result or inspect the generated PR and its dispatched CI.
7. Follow [registry setup](RELEASING.md#initial-registry-setup) before publishing
   the next release tag.

The shared workflow is referenced at `main`. Review changes to it as changes
that affect every SDK. Existing release tags do not run retroactively when a
workflow is installed. Keep published tags fixed.

## Checks and completion evidence

Run from `openapi` for a contract-tool change:

```sh
python validate.py
python -m unittest discover -s tests
```

Use the [generation commands](README.md#generate-an-sdk) and
[check_sdk.py](check_sdk.py) for language checks. Read each language README for
focused commands. Use `actionlint` to check changed workflow YAML.

Behavior checks must cover the affected user path. Existing SDK checks cover
authentication, wire field names, null versus omission, search unions, polling,
pagination, retries, uploads, downloads, and error responses.

Each SDK has `testdata/contract.json`. This repository has the shared reference
fixture at the same path. Generation does not copy those fixtures. Keep changed
wire responses consistent across affected fixtures and the application models.

For releases, follow [publication verification](RELEASING.md#verify-publication).
Record the source commit, artifact digest, registry version, and consumer
result. A build, push, upload acknowledgement, or green workflow alone does not
establish an installed-package result.

For documentation-only changes, check links, referenced files, commands, and
`git diff --check`. Report local checks, GitHub CI, package publication, and
application deployment separately. State the remaining blocker and saved
candidate when work is incomplete.

## Organization and profile changes

In `.github`, edit `profile/README.md` for the organization overview. The logo
used by that page is `assets/sandfish.png`. Shared guidance is in
`CONTRIBUTING.md` and `SUPPORT.md`; issue templates are in `.github/ISSUE_TEMPLATE`.
Repository descriptions, topics, and homepage URLs are GitHub settings.

The personal profile uses `azizollah1983/azizollah1983/README.md`. It is separate
from the organization profile. Verify profile changes on their public pages.

Repository pins and the organization avatar use the GitHub profile settings.
A logo in the README does not set the avatar. Domain verification requires the
TXT record that GitHub provides and access to the domain's DNS settings.
Verify the resulting public profile or verified-domain state after the change.

Keep installation examples, registry links, and preview status accurate.
Update the SDK README, affected examples, and relevant profile links after a
package release.

## Credentials and interrupted work

Read supplied credentials from the environment or a private temporary file.
Keep token values out of Git, remote URLs, documentation, command output, and
release artifacts. An npm configuration can reference `${NODE_AUTH_TOKEN}`
instead of containing the token. Remove task-created credential files after
use. Do not copy temporary credentials into Actions secrets when the planned
release method uses trusted publishing.

Inspect existing jobs, source revisions, and artifacts before restarting work.
Generation can take longer than a short command timeout. The generator permits
up to 30 minutes per invocation. Check the saved log and running process before
starting a replacement. Do not generate twice into the same SDK directory at
the same time.

If a workflow commit cannot be pushed, keep it in Git and report the missing
permission. Publish unrelated documentation from a clean branch based on the
remote when needed. Then incorporate that remote commit while preserving the
unpublished workflow change. Recheck the branch difference after any rebase.
