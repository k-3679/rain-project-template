# repo-rules

Configuration files and settings this template expects, so they can be
applied by script instead of clicked through in the GitHub UI. `apply-repo-rules.yml` applies
all of these automatically on `workflow_dispatch`.

## Files

| File | What | API it maps to |
|---|---|---|
| `branch-ruleset.main.json` | Protects `main`: no deletion, no force-push (or direct push), linear history, PR + 1 review required, stale reviews dismissed on new commits, must be up to date with `main` before merging, and must pass `Validation summary` | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `tag-ruleset.releases.json` | Protects `v*` tags from being created/moved/deleted by anyone outside the bypass list, so a shipped release can't be quietly rewritten. | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `repo-settings.json` | Squash-merge only, auto-delete head branches after merge, projects enabled, release immutability on. | `PATCH /repos/{owner}/{repo}` for everything except `immutable_releases`, which `apply-repo-rules.yml` applies separately via `PUT/DELETE /repos/{owner}/{repo}/immutable-releases` (it's not part of the repo PATCH body). |
| `actions-permissions.json` | Only GitHub-owned actions, Marketplace-verified actions, and anything under `k-3679/*` (our own reusable workflows) can run. Workflow token defaults to **read/write**. | `PUT /repos/{owner}/{repo}/actions/permissions` + `.../selected-actions` + `.../workflow` |

## Prerequisites

These are manual, one-time toggles in the GitHub UI. Nothing in `.github/repo-rules/` or
`apply-repo-rules.yml` can enable them via the API.

**Where:** repo → **Settings** → **Security** (sidebar) → **Advanced Security**. 

- **Dependabot alerts:** turn on (free).
- **Dependabot security updates:** turn on (free).
- **Code scanning:** required for the Trivy/CodeQL SARIF upload in `validate.yml` to work (requires a subscription).
- **Secret scanning:** turn on if available (requires a subscription).

You also need a token with admin rights on the repo. Either `gh auth login` for the manual
`gh api` commands below, or **short-lived** `ADMIN_TOKEN` secret for `apply-repo-rules.yml` (a basic `GITHUB_TOKEN` can't run the `gh api` commands in this workflow).

## Why

- **Rulesets over classic branch protection**, rulesets are the current GitHub mechanism,
  are fully API-driven (create/update/delete via REST), and support named bypass actors
  instead of an all-or-nothing admin override.
- **`required_status_checks` only lists `Validation summary`**, not the individual lint/Trivy/CodeQL/changelog
  jobs. That job depends on all of them (see `.github/workflows/validate.yml`), so its result already covers every check.
- **`actions-permissions.json` allow-lists `k-3679/*`** because every workflow in this template
  calls reusable workflows/actions from `k-3679/reusable-workflows`. Marketplace-verified +
  GitHub-owned actions cover everything else currently in use (`actions/checkout`, etc.). The default permission for the `GITHUB_TOKEN` is set to **read**. For writing, you need to specify the permissions at the workflow level (CI release workflow, Trivy/CodeQL SARIF scan report upload, setting up GH pages, etc).
- **`repo-settings.json` only allows squash-merge**, it's the only strategy that gives both a
  linear `main` (paired with `required_linear_history` in the branch ruleset) and one clean
  commit per PR, with no "wip"/"fix typo" noise from individual commits leaking into history.
  Merge commits keep every commit but make `main` non-linear; rebase merge is linear but still
  pollutes `main` with every intermediate commit.

## How

### Automated (recommended)

Run the **Apply repo rules** workflow (`Actions` tab -> `workflow_dispatch`) once,
after the repo created from this template has been [initialized](../workflows/init-repo.yml). It reads every file in this folder and applies it via the GitHub API.

`GITHUB_TOKEN` has no `administration` scope,
every call here needs repo admin rights. Add a PAT (classic with `admin:repo`, or
fine-grained with "Administration: write" on this repo) as a secret named `ADMIN_TOKEN`
before running it. Safe to re-run, every step is an upsert.

### Manual fallback

If you'd rather not store an admin-scoped PAT as a secret, apply the same files
yourself with the GitHub CLI:

```bash
gh api --method PUT repos/{owner}/{repo}/rulesets -H "Accept: application/vnd.github+json" \
  --input .github/repo-rules/branch-ruleset.main.json

gh api --method PUT repos/{owner}/{repo}/rulesets -H "Accept: application/vnd.github+json" \
  --input .github/repo-rules/tag-ruleset.releases.json

jq 'del(.immutable_releases)' .github/repo-rules/repo-settings.json \
  | gh api --method PATCH repos/{owner}/{repo} --input -

gh api --method PUT repos/{owner}/{repo}/immutable-releases

gh api --method PUT repos/{owner}/{repo}/actions/permissions \
  --input .github/repo-rules/actions-permissions.json
gh api --method PUT repos/{owner}/{repo}/actions/permissions/selected-actions \
  --input .github/repo-rules/actions-permissions.json
```

(`gh api --method PUT .../rulesets` here is shorthand. Creating and/or updating an existing
ruleset by name actually needs a `GET` first to find its `id`; `apply-repo-rules.yml` handles
that lookup for you)

### Things that can't / shouldn't be scripted

These require an interactive UI or aren't exposed over the GH REST API:

- **Enabling GitHub Advanced Security / private-repo code scanning:** on a private repo this
  is a paid feature, it must be turned on (or already covered by your plan) before the
  Trivy/CodeQL SARIF upload in `validate.yml` will succeed. On a public repo it's free and on
  by default.
- **Repository visibility (public/private) and repository deletion protections:** visibility
  can be scripted (`PATCH /repos/{owner}/{repo}` with `"private": true|false`), but changing
  it is disruptive enough that this template deliberately leaves it as a manual, deliberate
  choice at repo-creation time instead of something `apply-repo-rules.yml` flips silently.
- **Limiting how many branches/tags can be updated in a single push:** (Settings -> General ->
  Pushes) this is a GitHub Preview feature with no documented, stable REST field as
  of this writing, so there's nothing for `apply-repo-rules.yml` to call. Set it manually in the UI if you want it.
- **Org-level policies:** (if this repo ever moves into an org) org-wide required
  workflows, SSO enforcement, org secret access, those live outside a single repo's API
  surface.

### Any automation that needs to push straight to `main` or a `v*` tag

The bypass actor in both rulesets is `RepositoryRole: admin` (`actor_id: 5`), which only
covers actual users/tokens holding the repo's Admin role.

If you add a release/automation workflow that needs to push a version bump or tag directly
to a protected ref, give it its own admin-scoped PAT as a secret (same pattern as
`ADMIN_TOKEN` above) and use that
for the checkout/push/tag steps instead of `GITHUB_TOKEN`.
