# Release an SDK

## Initial registry setup

### Python

Create a PyPI account. Add a pending trusted publisher with these fields:

- Project: `sandfish-sdk`
- GitHub owner: `Sandfi-sh`
- Repository: `sandfish-python`
- Workflow: `release.yml`
- Environment: `pypi`

The first successful publish creates the project. A pending publisher does not
reserve its name. GitHub access does not grant PyPI access.

### TypeScript and JavaScript

Create the npm organization `sandfi-sh`. Publish the first checked package with
an authenticated npm session and `npm publish --access public`. Then configure
its trusted publisher:

- GitHub owner: `Sandfi-sh`
- Repository: `sandfish-typescript`
- Workflow: `release.yml`
- Environment: `npm`
- Allowed action: direct `npm publish`

Use npm 11.5.1 or later and Node 22.14.0 or later. Configure trust immediately
before the first automated publication. npm requires a new publisher to
complete its first publish within two days. GitHub-hosted runners provide the
OIDC identity used by this workflow.

### Go

Go needs no registry account. The module path is
`github.com/sandfi-sh/sandfish-go`. A version tag makes the release available to
the Go module proxy. Keep the module at the repository root.

## Prepare the candidate

Choose each SDK version independently. Use a patch for compatible fixes, a
minor version for additions, and a major version for breaking changes. During
the 0.x preview, use a new minor version for a breaking change.

From this repository, run these commands for the target SDK:

```sh
python release.py 0.1.1 --directory ../sandfish-python
python generate.py python --output ../sandfish-python
python generate.py python --output ../sandfish-python --check
python check_sdk.py ../sandfish-python
python release.py 0.1.1 --directory ../sandfish-python --check
```

Update the SDK changelog. Commit and push the checked candidate. Tag that exact
commit as `v0.1.1`, then push the tag. The language repository's `release.yml`
builds and tests the package before publication.

The initial version is `0.1.0`; substitute that version for the first release.
Create the `pypi` and `npm` environments in their repositories before tagging.

## Verify publication

Install the exact version into a clean consumer project. Run a public read,
such as listing plans or execution profiles. Check the package version and
source manifest. A successful workflow alone does not establish this result.

Publication can be retried. The workflows check the artifact digests when a
version is already present. Different bytes fail the release check. Never
replace an existing version with different code. Release a new patch if a
published package needs a correction.

The [Python](https://github.com/sandfi-sh/sandfish-python),
[TypeScript](https://github.com/sandfi-sh/sandfish-typescript), and
[Go](https://github.com/sandfi-sh/sandfish-go) READMEs contain consumer examples.
