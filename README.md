# rain-project-template

[![Bootstrap repo settings](https://github.com/k-3679/rain-project-template/actions/workflows/bootstrap.yml/badge.svg)](https://github.com/k-3679/rain-project-template/actions/workflows/bootstrap.yml)
[![Validate Changes](https://github.com/k-3679/rain-project-template/actions/workflows/validate.yml/badge.svg)](https://github.com/k-3679/rain-project-template/actions/workflows/validate.yml)
[![Changelog](https://img.shields.io/badge/changelog-CHANGELOG.md-blue)](CHANGELOG.md)

Template repository for new projects. Use it via GitHub's **"Use this template"**
button (or `gh repo create --template k-3679/rain-project-template`) instead of starting a
new repo from scratch.

- **Goal:** every repo created from this starts with the same baseline hygiene (changelog,
CI, security scanning, branch/tag protection) without copy/pasting it by hand each time,
and without pretending things are automated when they aren't.

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

 See [`.github/repo-rules/README.md`](.github/repo-rules/README.md#why) for the full reasoning
behind each rule this enforces.

## What you get
 
```
rain-project-template/
├── CHANGELOG.md              # Keep a Changelog, starts at [Unreleased]
├── .editorconfig
├── .gitattributes            # LF normalization
├── .gitignore
└── .github/
    ├── CODEOWNERS
    ├── SECURITY.md
    ├── SETUP.md               # one-time setup checklist
    ├── PULL_REQUEST_TEMPLATE.md
    ├── dependabot.yml         # keeps project dependecies up to date
    ├── ISSUE_TEMPLATE/
    │   ├── config.yml
    │   ├── bug_report.yml
    │   └── feature_request.yml
    ├── workflows/
    │   ├── setup-checklist.yml # workflow_dispatch, one-time run, self-deleting
    │   ├── validate.yml        # PRs to main: lint (opt-in) + Trivy + CodeQL + changelog
    │   └── bootstrap.yml       # workflow_dispatch, applies everything under repo-rules/
    └── repo-rules/            # what bootstrap.yml applies
        ├── README.md
        ├── branch-ruleset.main.json
        ├── tag-ruleset.releases.json
        ├── repo-settings.json
        └── actions-permissions.json
```

## Workflows
 
| Workflow | Runs on | What it does |
| --- | --- | --- |
| [`setup-checklist.yml`](.github/workflows/setup-checklist.yml) | Manual, once per new repo | Opens [`SETUP.md`](.github/SETUP.md) as an issue, then deletes itself and `SETUP.md`. |
| [`validate.yml`](.github/workflows/validate.yml) | PRs to `main`, pushes, weekly, manual | Lint (opt-in per language), Trivy, CodeQL, and a changelog check on PRs. The `Validation summary` job needs all of them and is the only required status check, so new linters and CodeQL languages are gated without editing the ruleset. |
| [`bootstrap.yml`](.github/workflows/bootstrap.yml) | Manual | Applies everything in [`repo-rules/`](.github/repo-rules/) (branch and tag rulesets, repo settings, Actions permissions) over GH REST API. Needs an `ADMIN_TOKEN` secret. Every step is an upsert, so it is safe to re-run. |
 
All CI here calls into [`k-3679/reusable-workflows`](https://github.com/k-3679/reusable-workflows)
rather than duplicating logic.

## Using this template

1. Create the new repo from this template on GitHub (GitHub's **"Use this template"** button).
2. Actions tab → run **Setup checklist**. The workflow opens a **"📝 Repo setup checklist"** issue with the
   full checklist of one time required manual setups. Work through the issue, mark your finished tasks, and close the issue when done.

## Design principles

- **Script what's actually scriptable.** `bootstrap.yml` is real automation against the
  GitHub REST API, and it's safe to reuse.
- **Be honest about what isn't.** Anything that needs a plan/billing decision, a one-time
  interactive choice, or lives outside a single repo's API surface is documented in
  `repo-rules/README.md`. 
- **No lint job runs until it has something to lint.** Avoids the classic template-repo
  failure mode of red CI from the first commit.
