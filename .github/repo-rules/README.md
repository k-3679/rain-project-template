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

## How

### Automatic (recommended)

Run the **Bootstrap repo settings** workflow (`Actions` tab -> `workflow_dispatch`) once,
after the repo created from this template has been pushed. It reads every file in this
folder and applies it via the GitHub API using the workflow's own token
(`permissions: administration: write`). Safe to re-run - every step is an upsert.

### Manual fallback

If you don't want to grant `administration: write` to a workflow, apply the same files
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

### If the release workflow gets blocked by the new branch ruleset

The bypass actor in both rulesets is `RepositoryRole: admin` (`actor_id: 5`) with
`bypass_mode: "always"`, which is what lets the default `GITHUB_TOKEN` push release commits
and tags straight to `main` without a PR, as long as the workflow declares
`permissions: contents: write`. Test this on a real release after applying the rulesets. If
pushes still get rejected, the usual fix is switching the release job to a fine-grained PAT
(stored as a secret) that has admin on the repo, instead of relying on `GITHUB_TOKEN`.
