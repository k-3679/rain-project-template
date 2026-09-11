# rain-project-template

Template repository for new `k-3679` projects. Use it via GitHub's **"Use this template"**
button (or `gh repo create --template k-3679/rain-project-template`) instead of starting a
new repo from scratch.

Goal: every repo created from this starts with the same baseline hygiene - changelog,
CI, security scanning, branch/tag protection - without copy-pasting it by hand each time,
and without pretending things are automated when they aren't.

## What you get

```
rain-project-template/
├── CHANGELOG.md              # Keep a Changelog, starts at [Unreleased]
├── .editorconfig
├── .gitignore
└── .github/
    ├── CODEOWNERS
    ├── SECURITY.md
    ├── PULL_REQUEST_TEMPLATE.md
    ├── dependabot.yml         # keeps GitHub Actions versions current
    ├── ISSUE_TEMPLATE/
    │   ├── config.yml
    │   ├── bug_report.yml
    │   └── feature_request.yml
    ├── workflows/
    │   ├── validate.yml       # runs on PRs to main: lint (opt-in) + security scan + changelog check
    │   └── bootstrap.yml      # workflow_dispatch, applies everything under repo-rules/
    └── repo-rules/            # what bootstrap.yml applies - see its own README
        ├── README.md
        ├── branch-ruleset.main.json
        ├── tag-ruleset.releases.json
        ├── repo-settings.json
        └── actions-permissions.json
```

All CI here calls into [`k-3679/reusable-workflows`](https://github.com/k-3679/reusable-workflows)
rather than duplicating logic - update workflows there and every repo built from this
template picks it up.

## Using this template

1. Create the new repo from this template on GitHub.
2. Clone it, replace this README, update `CHANGELOG.md`'s project name if you keep the
   Keep a Changelog header.
3. In `.github/workflows/validate.yml`, set `LINTERS` to whatever languages the project
   actually uses (e.g. `'["node"]'`) - it ships empty on purpose so a brand-new repo
   doesn't start with a failing check for a language it doesn't have yet.
4. Push to `main` once, then run the **Bootstrap repo settings** workflow
   (`Actions` tab -> `workflow_dispatch`) to apply branch/tag rulesets, merge-strategy
   settings, and the Actions allow-list. See [`.github/repo-rules/README.md`](.github/repo-rules/README.md)
   for exactly what it does, why, and the handful of things (like GHAS licensing on
   private repos) that genuinely can't be scripted and need a manual decision.

## Design principles

- **Script what's actually scriptable.** `bootstrap.yml` is real automation against the
  GitHub REST API, not a checklist pretending to be a workflow.
- **Be honest about what isn't.** Anything that needs a plan/billing decision, a one-time
  interactive choice, or lives outside a single repo's API surface is documented in
  `repo-rules/README.md` instead of silently skipped or faked.
- **No lint job runs until it has something to lint.** Avoids the classic template-repo
  failure mode of red CI from the first commit.
