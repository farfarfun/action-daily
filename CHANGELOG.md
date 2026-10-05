# Changelog

All notable changes to this repository are documented in this file.

## Unreleased

### Fixed

- Stop the Codex audit with a non-zero status when one or more repository clones,
  Codex runs, or result parses fail, preventing incomplete audit results from being
  used to create issues.
- Do not write the configured custom OpenAI endpoint URL to audit logs.

### Added

- Document local installation and authentication prerequisites for the GitHub CLI
  and Codex CLI.

## Initial release

### Added

- Scheduled Gitee mirroring and rolling Codex compliance audits for farfarfun
  repositories.
