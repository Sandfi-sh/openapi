# Initial SDK release record, 21 October 2026

This is a historical setup and verification record. It does not establish
current deployment or registry state. Use [the maintenance guide](../MAINTAINING.md)
for procedures and recheck remote state before continuing this work.

## Verified source and releases

The public contract contains 117 supported operations. It uses OpenAPI
Generator 7.26.0 and the checksum in `generator.json`.

| Item | Verified identity |
|---|---|
| Application API candidate | `46b52f2dda93e921cae77795b95326d6ef5fd591`, branch `feat/public-sdks` |
| Public schema SHA-256 | `605f917489f5583541c859e975595cd599c3e526f285adbb2d8ba944ff8df39f` |
| npm `@sandfi-sh/sdk@0.1.0` | Tag `v0.1.0` at `8be4a4f0605c0a87e14edc095c00a40a1d43f945` |
| Go `v0.1.0` | Tag at `1b3d8ae7f9ac045c33af69e6e932b9201935c95a` |
| Python source | Published at `0463f885cec84901ed46c480b90ee7b95f8fe828`; PyPI publication pending |
| npm example instructions | `fb3f7bd1a7984cb249b6f2195da16b134c96e303` |

The npm archive SHA-256 is
`ff70cdf47b8fd129069bec87b397c745d30a473fc945509d2e703786d553ccee`.
Its registry integrity is:

```text
sha512-9x2vKOGgFA538muVfVfIpXO1FZYIt1A8ZIxWAsiDUXC43FUvQrtEa6z1n5c3C0JPkEAUoi9hcaLajh7YDl3MJQ==
```

## Verification completed

- All three SDKs passed their client checks and reproducible generation checks.
- Python and TypeScript each passed 11 client tests. Go passed its tests and
  `go vet`.
- A built Python wheel installed in an isolated consumer and read public plans.
- The Go release installed through the module proxy and read public plans.
- npm accepted the upload before it served the package. A later registry read
  confirmed the archive digest and `latest: 0.1.0`.
- A fresh npm installation matched the source manifest and retrieved four
  public plans. The TypeScript source and example instructions were published.
- The application check passed 4,369 unit tests, 929 integration tests,
  428 frontend tests, and 88 browser tests, plus service checks. The optional
  local EML corpus test was skipped because its corpus was not configured.
- The application check used `TC_MAX_TRIES=600` after a PostgreSQL startup
  timeout. This was a local startup allowance, not a change to application code.
- Prepared GitHub workflows passed `actionlint` locally.

## State checked after npm publication

The npm registry served version `0.1.0`, and the Go proxy served `v0.1.0`.
The PyPI endpoint for `sandfish-sdk` returned HTTP 404.

GitHub reported no installed workflows in `openapi`, `sandfish-python`,
`sandfish-typescript`, or `sandfish-go`. Each local repository had one pending
workflow commit. The setup GitHub token lacked the `workflow` scope. Preserve
those commits; documentation rebases can change their hashes.

Actions PR creation was enabled at both organization and repository levels.
The Python `pypi` and TypeScript `npm` release environments were created.
PyPI pending-publisher setup and npm trusted-publisher setup were unfinished.

The deployed `/docs/openapi.json` response did not contain the public-contract
marker or `X-Sandfish-Revision`. The checked application branch had been pushed,
but its public export had not been verified in production. `source.json`
therefore retained `status: candidate`.

The organization and personal profile READMEs were published. Repository pins
and GitHub domain verification remained unfinished. The README logo was
published as an asset; this does not prove an organization avatar change.

## Continue the setup

1. Recheck repository state and the pending workflow commits.
2. Obtain GitHub workflow-write permission and follow the maintenance guide's
   [Actions activation procedure](../MAINTAINING.md#activate-and-maintain-actions).
3. Complete the registry setup in [RELEASING.md](../RELEASING.md).
4. Publish Python's first checked version and verify it from PyPI.
5. Validate npm trusted publishing with the next authorized release. Keep
   `0.1.0` and its source tag fixed.
6. After an authorized application merge and deployment, verify the public
   export and its revision. Resolve the metadata-only synchronization case
   described in the maintenance guide.
7. Complete profile pins and domain verification through GitHub and DNS settings.

The original checkout used sibling repositories under `sandfish-sdks` beside
the application checkout. Future work can use fresh clones. Old temporary
tooling and credential files are not prerequisites.
