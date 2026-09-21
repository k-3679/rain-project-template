# rain-project-template

[![Setup repo](https://github.com/k-3679/rain-project-template/actions/workflows/repo-setup.yml/badge.svg)](https://github.com/k-3679/rain-project-template/actions/workflows/repo-setup.yml)
[![Validate Changes](https://github.com/k-3679/rain-project-template/actions/workflows/validate.yml/badge.svg)](https://github.com/k-3679/rain-project-template/actions/workflows/validate.yml)
[![Changelog](https://img.shields.io/badge/changelog-CHANGELOG.md-blue)](CHANGELOG.md)

Template repository for new projects. Use it via GitHub's **"Use this template"**
button (or `gh repo create --template k-3679/rain-project-template`) instead of starting a
new repo from scratch.

- **Goal:** every repo created from this starts with the same baseline hygiene (changelog,
CI, security scanning, branch/tag protection) without manual copy/pasting each time,
and without pretending things are automated when they aren't.

## Template structure

```
rain-project-template/
├── CHANGELOG.md                 # Keep a Changelog, starts at [Unreleased]
├── .editorconfig
├── .gitattributes               # LF normalization
├── .gitignore
└── .github/
    ├── CODEOWNERS
    ├── SECURITY.md
    ├── SETUP.md                 # manual checklist, opened as an issue
    ├── PULL_REQUEST_TEMPLATE.md
    ├── dependabot.yml           # keeps project dependencies up to date
    ├── ISSUE_TEMPLATE/
    │   ├── config.yml
    │   ├── bug_report.yml
    │   └── feature_request.yml
    ├── scripts/                  # temporary init/setup scripts
    │   ├── seed-repo.py         
    │   ├── build-languages.sh  
    │   ├── write-validate.py   
    │   └── write-dependabot.py
    ├── workflows/
    │   ├── template-init.yml   
    │   ├── validate.yml         
    │   └── repo-setup.yml       
    └── repo-rules/              # rules and configs applied to repos created from this template
        ├── README.md
        ├── branch-ruleset.main.json
        ├── tag-ruleset.releases.json
        ├── repo-settings.json
        ├── actions-permissions.json
        └── security-settings.json
```

## Workflows

| Workflow | Runs on | What it does |
| --- | --- | --- |
| [`template-init.yml`](.github/workflows/template-init.yml) | First push to `main` | Opens [`SETUP.md`](.github/SETUP.md) as an issue, runs [`seed-repo.py`](.github/scripts/seed-repo.py) to write `README.md`, `CODEOWNERS` and `CHANGELOG.md` for the new repo, then deletes itself, `SETUP.md` and `scripts/seed-repo.py`. Aborts if run on the template itself. |
| [`validate.yml`](.github/workflows/validate.yml) | PRs and pushes to `main`, weekly, manual | Lint (per language), Trivy, CodeQL, and a changelog check on PRs. A `check-init` job skips everything while `template-init.yml` is still present. The `Validation summary` job needs all of them and is the only required status check, so new linters and CodeQL languages are gated without editing the ruleset. |
| [`repo-setup.yml`](.github/workflows/repo-setup.yml) | Manual | Two jobs, in order: `wire-languages` runs the `scripts/build-languages.sh`, `scripts/write-validate.py` and `scripts/write-dependabot.py` helpers to set [`validate.yml`](./.github/workflows/validate.yml)'s linters/CodeQL languages and uncomment the matching [`dependabot.yml`](.github/dependabot.yml) ecosystem(s) for whichever languages you check (only languages supported by both the linter and CodeQL are offered), then deletes those helper scripts, and pushes to `main`. It does nothing if already wired up. `apply-rules` then applies everything in [`repo-rules/`](.github/repo-rules/) (branch and tag rulesets, repo settings, Actions permissions, security settings) over GH REST API. Needs an `ADMIN_TOKEN` secret. Safe to re-run. |

All CI here calls [`k-3679/reusable-workflows`](https://github.com/k-3679/reusable-workflows)
rather than duplicating logic.

## Using this template

1. Create the new repo from this template on GitHub (**"Use this template"** button).
2. Creating the repo pushes an initial commit to `main`, which triggers
   [**Initialize repository**](.github/workflows/template-init.yml) automatically. It fills in `README.md`, `.github/CODEOWNERS`, `CHANGELOG.md`, and opens a **"📝 Repo setup checklist"** issue for the new repo.
3. Follow the checklist in the issue, checking off each task, and close it when done.

## Branching & release flow

This template is built around **GitHub Flow**: `main` is always deployable, every change
lands through a short-lived branch and a PR, no `develop` branch, no long-lived release
branches.

- Branch off `main`, commit, open a PR.
- PR needs 1 approval, resolved review threads, and a passing `Validation summary` check
  before it can merge (`branch-ruleset.main.json`).
- **Squash merge only:** one commit per PR, linear `main` history, one changelog entry (`Unreleased`) to
  match the squashed commit (`repo-settings.json`). Every merged commit in `main` is a ready to release (revertible) feature.
- Feature branch is deleted automatically on merge.
- Tag a release straight off `main`, manually or via a release workflow (recommended).    `tag-ruleset.releases.json` locks that tag from being moved or deleted afterwards.

See [`.github/repo-rules/README.md`](.github/repo-rules/README.md#why) for the applied rules and why they exist.

## Changelog

View [CHANGELOG.md](CHANGELOG.md) for version history and changes.
