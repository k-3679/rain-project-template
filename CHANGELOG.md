# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Repo scaffold: README, `.gitignore`, `.editorconfig`, `CODEOWNERS`, `SECURITY.md`, PR template, issue templates (bug report, feature request), `dependabot.yml`.
- `validate.yml` workflow: security scan and changelog validation on every PR to `main`, plus opt-in lint jobs (php/python/node/go/rust/c) wired to `k-3679/reusable-workflows` but disabled by default until a project actually uses that language.
- `bootstrap.yml` workflow: applies everything under `.github/repo-rules/` (branch/tag rulesets, merge-strategy settings, Actions permissions) via the GitHub API, using an admin-scoped PAT (`ADMIN_TOKEN` secret).
- `.github/repo-rules/`: JSON definitions for the `main` branch ruleset, `v*` tag ruleset, repo settings, and Actions permissions, plus a README documenting what each does, why, prerequisites (Dependabot/code scanning enablement), and the manual `gh api` fallback.
- `repo-settings.json`: `immutable_releases` flag; `bootstrap.yml` applies it via `PUT/DELETE /repos/{owner}/{repo}/immutable-releases` since it's not part of the repo PATCH body.
- README: step to manually enable the `.github/repo-rules/README.md` prerequisites after running `bootstrap.yml`.
- `validate.yml`: new `codeql` job calling a new `k-3679/reusable-workflows/.github/workflows/codeql.yml` reusable workflow (converted from GitHub's generated "CodeQL Advanced" template), replacing CodeQL default setup so analysis can be driven from this workflow. Requires default setup to be switched off in Settings -> Code security -> Code scanning first.

### Changed

- `actions-permissions.json`: `default_workflow_permissions` from `read` to `write`.
- `validate.yml`: `summary` job now prints the Trivy findings count and a direct link to the scan results (PR link, or branch-filtered Security tab link on push), instead of relying on manually switching the branch dropdown on the Code scanning alerts page.
- `validate.yml`: `changelog` job now skips entirely on Dependabot PRs (`github.actor == 'dependabot[bot]'`) instead of failing the required "Validate changelog" check, since Dependabot never touches `CHANGELOG.md`.
- `validate.yml`: `security` job renamed to `trivy` (now calls `trivy.yml` instead of `security-scan.yml`); `Security scan` check renamed to `Trivy scan`.
- `validate.yml`: `changelog` job has `continue-on-error: true` again, for testing.
- `validate.yml`: `actions/checkout` bumped from `v4` to `v7`.

### Fixed

- `validate.yml`: `security` job was missing the `actions: read` permission required by `codeql-action/upload-sarif`, causing the SARIF upload to fail with "Resource not accessible by integration".
- `validate.yml`: `summary` job's scan-results link went to the PR's Conversation tab on PR-triggered runs instead of the actual findings; now links to Code scanning alerts filtered by `pr:<number>`.
- `branch-ruleset.main.json`: `required_status_checks` had `"CodeQL Scan"` (capital S) but the actual job is named `CodeQL scan` (lowercase); the mismatch left that required check permanently stuck on "Expected, waiting for status to be reported" since the context could never match.

