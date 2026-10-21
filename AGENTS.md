# Agent instructions

Read [MAINTAINING.md](MAINTAINING.md) before changing the contract, generator,
automation, SDKs, or organization presentation. Use [README.md](README.md) for
generation commands and [RELEASING.md](RELEASING.md) for registry operations.

- Check the working tree, remote revision, and unpublished commits first.
- Keep API definitions in the application repository. Import its public export.
- Keep generated output reproducible and preserve maintained client files.
- Run contract-tool checks and each affected SDK check for behavior changes.
- Check workflow YAML with `actionlint` when workflow files change.
- Check links, source references, commands, and `git diff --check` for prose changes.
- Keep credentials out of documentation, Git, and tool output.
- Update the owning guide when a change establishes a reusable procedure.
- Verify registry installation and an API call before confirming a release.
- Keep historical observations in dated records. Recheck them before resuming.

Use short, direct sentences, active voice, and consistent technical terms.
