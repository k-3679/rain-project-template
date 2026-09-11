# repo-rules

Machine-readable definitions of the repo settings this template expects, so they can be
applied by script instead of clicked through in the GitHub UI. `bootstrap.yml` applies all
of these automatically on `workflow_dispatch` - this folder is what it reads, and it's also
the fallback if you'd rather apply things by hand (or `bootstrap.yml` can't do something,
e.g. it's a plan/billing-gated setting).

## Files

| File | What | API it maps to |
|---|---|---|
| `branch-ruleset.main.json` | Protects `main`: no deletion, no force-push, linear history, PR + 1 review required, must pass `Security scan` and `Validate changelog`. | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `tag-ruleset.releases.json` | Protects `v*` tags from being created/moved/deleted by anyone outside the bypass list, so a shipped release can't be quietly rewritten. | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `repo-settings.json` | Squash-merge only, auto-delete head branches after merge, wiki/projects tabs off (we don't use them). | `PATCH /repos/{owner}/{repo}` |
| `actions-permissions.json` | Only GitHub-owned actions, Marketplace-verified actions, and anything under `k-3679/*` (our own reusable workflows) can run. Workflow token defaults to read-only. | `PUT /repos/{owner}/{repo}/actions/permissions` + `.../selected-actions` |

## Prerequisites

These are manual, one-time toggles in the GitHub UI. Nothing in `.github/repo-rules/` or
`bootstrap.yml` can enable them via the API.

**Where:** repo → **Settings** → **Security** (sidebar) → **Advanced Security**. If your
repo doesn't show that link, look for **Code security and analysis** instead - same page,
older name.

- **Dependabot version updates** - already works, nothing to enable. Driven entirely by
  `dependabot.yml`, which ships in this template.
- **Dependabot alerts** - turn on. Free for public and private repos.
- **Dependabot security updates** - turn on (requires alerts to be on first). Free for public
  and private repos.
- **Code scanning** - required for the Trivy SARIF upload in `security-scan.yml` to work.
  Free and on by default for public repos. For a private repo it needs GitHub Advanced
  Security enabled, which is a paid add-on on most plans. If it's not available, add
  `continue-on-error: true` to the SARIF upload step, or make the repo public.
- **Secret scanning** - turn on if available. Same public/private split as code scanning.
  Not wired into any workflow here, just worth having on.

You also need a token with admin rights on the repo - either `gh auth login` for the manual
`gh api` commands below, or an `ADMIN_TOKEN` secret for `bootstrap.yml`. `GITHUB_TOKEN` can
never provide this (see "Automatic" below).

## Why

- **Rulesets over classic branch protection** - rulesets are the current GitHub mechanism,
  are fully API-driven (create/update/delete via REST), and support named bypass actors
  instead of an all-or-nothing admin override.
- **`required_status_checks` only lists `Security scan` and `Validate changelog`**, not lint -
  lint jobs are opt-in per-project (see `.github/workflows/validate.yml`), so requiring them
  here would block merges on a check that may never run.
- **`actions-permissions.json` allow-lists `k-3679/*`** because every workflow in this template
  calls reusable workflows/actions from `k-3679/reusable-workflows`. Marketplace-verified +
  GitHub-owned actions cover everything else currently in use (`actions/checkout`, etc.).
- **`repo-settings.json` only allows squash-merge** - it's the only strategy that gives both a
  linear `main` (paired with `required_linear_history` in the branch ruleset) and one clean
  commit per PR, with no "wip"/"fix typo" noise from individual commits leaking into history.
  Merge commits keep every commit but make `main` non-linear; rebase merge is linear but still
  pollutes `main` with every intermediate commit.

## How

### Automatic (recommended)

Run the **Bootstrap repo settings** workflow (`Actions` tab -> `workflow_dispatch`) once,
after the repo created from this template has been pushed. It reads every file in this
folder and applies it via the GitHub API.

`GITHUB_TOKEN` has no `administration` scope, so this can't run on the default token -
every call here needs repo admin rights. Add a PAT (classic with `admin:repo`, or
fine-grained with "Administration: write" on this repo) as a secret named `ADMIN_TOKEN`
before running it. Safe to re-run - every step is an upsert.

### Manual fallback

If you'd rather not store an admin-scoped PAT as a secret, apply the same files
yourself with the GitHub CLI:

```powershell
gh api --method PUT repos/{owner}/{repo}/rulesets -H "Accept: application/vnd.github+json" `
  --input .github/repo-rules/branch-ruleset.main.json

gh api --method PUT repos/{owner}/{repo}/rulesets -H "Accept: application/vnd.github+json" `
  --input .github/repo-rules/tag-ruleset.releases.json

gh api --method PATCH repos/{owner}/{repo} `
  --input .github/repo-rules/repo-settings.json

gh api --method PUT repos/{owner}/{repo}/actions/permissions `
  --input .github/repo-rules/actions-permissions.json
gh api --method PUT repos/{owner}/{repo}/actions/permissions/selected-actions `
  --input .github/repo-rules/actions-permissions.json
```

(`gh api --method PUT .../rulesets` here is shorthand - creating vs. updating an existing
ruleset by name actually needs a `GET` first to find its `id`; `bootstrap.yml` handles that
lookup for you.)

### Things that can't be scripted

These require an interactive decision or aren't exposed over the REST API at all - the
template doesn't pretend otherwise:

- **Enabling GitHub Advanced Security / private-repo code scanning.** On a private repo this
  is a paid feature; it must be turned on (or already covered by your plan) before the
  security-scan workflow's SARIF upload will succeed. On a public repo it's free and on by
  default, nothing to do.
- **Repository visibility (public/private) and repository deletion protections** - visibility
  can be scripted (`PATCH /repos/{owner}/{repo}` with `"private": true|false`), but changing
  it is disruptive enough that this template deliberately leaves it as a manual, deliberate
  choice at repo-creation time instead of something `bootstrap.yml` flips silently.
- **Org-level policies** (if this repo ever moves into an org) - e.g. org-wide required
  workflows, SSO enforcement, org secret access - those live outside a single repo's API
  surface.

### Any automation that needs to push straight to `main` or a `v*` tag

The bypass actor in both rulesets is `RepositoryRole: admin` (`actor_id: 5`), which only
covers actual users/tokens holding the repo's Admin role - it does **not** reliably cover
the default `GITHUB_TOKEN`. Pushes made with `GITHUB_TOKEN` are attributed to the
`github-actions[bot]` app identity, not to a user with the Admin role, so whether it's
treated as bypass-eligible isn't guaranteed by anything documented here - don't rely on it.

If you add a release/automation workflow that needs to push a version bump or tag directly
to a protected ref, give it its own admin-scoped PAT as a secret (same pattern as
`ADMIN_TOKEN` above - a separate secret per workflow keeps blast radius smaller) and use that
for the checkout/push/tag steps instead of `GITHUB_TOKEN`. That's an actual Admin-role actor,
so the existing bypass config covers it unambiguously - no need to test-and-hope.
