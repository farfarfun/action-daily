# Changelog

All notable changes to this repository are documented in this file.

## Unreleased

### Fixed

- Stop the Codex audit with a non-zero status when one or more repository clones,
  Codex runs, or result parses fail, preventing incomplete audit results from being
  used to create issues.
- Do not write the configured custom OpenAI endpoint URL to audit logs.
- Build a minimal environment for the Codex subprocess instead of forwarding the
  whole job environment, so `ORG_PAT`/`GH_TOKEN` are no longer reachable from a
  sandboxed `codex exec` process reading arbitrary (possibly prompt-injected)
  repository content.
- Treat a failed `chmod -R a-w` as a hard failure instead of ignoring its exit
  code: previously a failed write-protection step still let `codex exec
  --sandbox danger-full-access` run against a writable clone.
- Stop collapsing a failed `gh issue list` call into "no open issue" in
  `codex_audit_cursor.py` and `file_codex_audit_issues.py`; a `gh` failure now
  aborts the batch-selection step and makes issue creation skip (rather than
  duplicate) the affected repository.
- Lower the `codex-find-issues.yml` Python floor from 3.12 to the
  organization-wide 3.10 baseline; the scripts never used any 3.11/3.12-only
  syntax.

### Added

- Document local installation and authentication prerequisites for the GitHub CLI
  and Codex CLI.
- Document the actual `codex-fix-issues.yml` / `merge-automation-prs.yml` PR
  and label flow in the README (it opens a PR and labels `fix-proposed`, it
  does not commit straight to the default branch or close the issue itself).

## Initial release

### Added

- Scheduled Gitee mirroring and rolling Codex compliance audits for farfarfun
  repositories.
