# rain-project-template

Template repository for new `k-3679` projects. Use it via GitHub's **"Use this template"**
button (or `gh repo create --template k-3679/rain-project-template`) instead of starting a
new repo from scratch.

**Goal:** every repo created from this starts with the same baseline hygiene (changelog,
CI, security scanning, branch/tag protection) without copy/pasting it by hand each time,
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
rather than duplicating logic.

## Using this template

1. Create the new repo from this template on GitHub.
2. Clone it, replace this README, update `CHANGELOG.md`'s project name if you keep the
   Keep a Changelog header.
3. In `.github/workflows/validate.yml`, update the `lint` job's `if:` and `with.linters:`
   to whatever languages the project actually uses (e.g. `'["node"]'` in both places).
   It comes empty on purpose so a brand-new repo doesn't start with a failing check for a
   language it doesn't have yet. Set `continue-on-error` to **false** for the `changelog` job.
   Also update the `codeql` job's `with.languages:` to match the languages you actually use. See [documentation](https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/codeql-code-scanning-for-compiled-languages).
4. Push to `main` once, then run the **Bootstrap repo settings** workflow
   (`Actions` tab -> `workflow_dispatch`) to apply branch/tag rulesets, merge-strategy
   settings, and the Actions allow-list. See [`.github/repo-rules/README.md`](.github/repo-rules/README.md)
   for exactly what it does, why, and the handful of things (like GHAS licensing on
   private repos) that genuinely can't be scripted and need a manual decision.
5. Manually enable the prerequisites listed in [`.github/repo-rules/README.md`](.github/repo-rules/README.md#prerequisites)
   (Dependabot alerts, Dependabot security updates, code scanning, secret scanning) plus
   anything else called out there under "Things that can't be scripted".

## Design principles

- **Script what's actually scriptable.** `bootstrap.yml` is real automation against the
  GitHub REST API, and it's safe to reuse.
- **Be honest about what isn't.** Anything that needs a plan/billing decision, a one-time
  interactive choice, or lives outside a single repo's API surface is documented in
  `repo-rules/README.md`.
- **No lint job runs until it has something to lint.** Avoids the classic template-repo
  failure mode of red CI from the first commit.
