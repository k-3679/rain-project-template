# repo-rules

Configuration files and settings this template expects, so they can be
applied by script instead of clicked through in the GitHub UI. The `apply-rules` job in
`repo-setup.yml` applies all of these automatically on `workflow_dispatch`.

## Files

| File | What | API it maps to |
|---|---|---|
| `branch-ruleset.main.json` | Protects `main`: no deletion, no force-push (or direct push), linear history, PR + 1 review required, stale reviews dismissed on new commits, must be up to date with `main` before merging, and must pass `Validation summary` | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `tag-ruleset.releases.json` | Protects `v*` tags from being created/moved/deleted by anyone outside the bypass list, so a shipped release can't be quietly rewritten. | `POST/PUT /repos/{owner}/{repo}/rulesets` |
| `repo-settings.json` | Squash-merge only, auto-delete head branches after merge, projects enabled, release immutability on. | `PATCH /repos/{owner}/{repo}` for everything except `immutable_releases`, which `repo-setup.yml` applies separately via `PUT/DELETE /repos/{owner}/{repo}/immutable-releases` (it's not part of the repo PATCH body). |
| `actions-permissions.json` | Only GitHub-owned actions, Marketplace-verified actions, and anything under `k-3679/*` (our own reusable workflows) can run. Workflow token defaults to **read**. | `PUT /repos/{owner}/{repo}/actions/permissions` + `.../selected-actions` + `.../workflow` |
| `security-settings.json` | Dependabot alerts, Dependabot security updates, secret scanning + push protection, code scanning (Advanced Security). | `PUT /repos/{owner}/{repo}/vulnerability-alerts` + `.../automated-security-fixes` + `PATCH /repos/{owner}/{repo}` (`security_and_analysis`) |

## Prerequisites

You need a token with admin rights on the repo. Either `gh auth login` for the manual
`gh api` commands below, or **short-lived** `ADMIN_TOKEN` secret for the `apply-rules` job in
`repo-setup.yml` (a basic `GITHUB_TOKEN` can't run the `gh api` commands in that job).

## Why

- **Rulesets over classic branch protection**, rulesets are the current GitHub mechanism,
  are fully API-driven (create/update/delete via REST), and support named bypass actors
  instead of an all-or-nothing admin override.
- **`required_status_checks` only lists `Validation summary`**, not the individual lint/Trivy/CodeQL/changelog
  jobs. That job depends on all of them (see `.github/workflows/validate.yml`), so its result already covers every check.
- **`require_last_push_approval` (*"the most recent push must be approved by someone other than the person who pushed it"*) is `false`** because `dismiss_stale_reviews_on_push` is already `true`: dismissing stale reviews forces a fresh approval after *every* push, not just when
  the last pusher happens to be the approver. Turning both on adds no extra protection, just an
  extra re-approval even when a different reviewer pushes a trivial fixup.

   <details>
    <summary><b>decision flow diagram</b></summary>

    ```mermaid
    flowchart TD
        A["Commit 1 pushed"] --> B["Reviewer R approves"]
        B --> C["Commit 2 pushed"]
        C --> D{"Who pushed commit 2?"}

        D -->|"Non-approver (PR author)"| E{"dismiss_stale_reviews_on_push?"}
        E -->|"true"| F["R's approval is cleared"]
        E -->|"false"| G["R's approval still stands"]
        F --> H["Not mergeable, needs re-review"]
        G --> I["Mergeable"]

        D -->|"R (the same approver)"| J{"dismiss_stale_reviews_on_push?"}
        J -->|"true"| K["R's approval is cleared"]
        J -->|"false"| L{"require_last_push_approval?"}
        K --> M["Not mergeable"]
        L -->|"true"| N["R's approval discounted for R's own push"]
        L -->|"false"| O["R's stale approval still counts"]
        N --> P["Not mergeable, needs a different approver"]
        O --> Q["Mergeable (self-review loophole)"]

        H --> R2["R re-approves commit 2"]
        R2 --> S["R is not the pusher of commit 2, self-review rule doesn't apply"]
        S --> T["Mergeable"]
    ```

    </details>
    <br>

- **`actions-permissions.json` allow-lists `k-3679/*`** because every workflow in this template
  calls reusable workflows/actions from `k-3679/reusable-workflows`. Marketplace-verified +
  GitHub-owned actions cover everything else currently in use. The default permission for the `GITHUB_TOKEN` is set to **read**. For writing, you need to specify the permissions at the workflow level (CI release workflow, Trivy/CodeQL SARIF scan report upload, setting up GH pages, etc).
- **`repo-settings.json` only allows squash-merge**, it's the only strategy that gives both a
  linear `main` (paired with `required_linear_history` in the branch ruleset) and one clean
  commit per PR, with no "wip"/"fix typo" noise from individual commits leaking into history.
  Merge commits keep every commit but make `main` non-linear; rebase merge is linear but still
  pollutes `main` with every intermediate commit.
- **`immutable_releases: true`** locks a release's assets and tag the moment it's published: no editing/deleting assets, no moving/deleting the tag while the release exists, and the tag name can't be reused even if the repo is deleted and
  recreated.

## How

### Automated (recommended)

Run the **Setup repo** workflow (`Actions` tab -> `workflow_dispatch`) once,
after the repo created from this template has been [initialized](../workflows/template-init.yml). Its
`apply-rules` job reads every file in this folder and applies it via the GitHub API, after the
`wire-languages` job wires up `validate.yml`/`dependabot.yml` for whichever languages you checked.

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

gh api --method PUT repos/{owner}/{repo}/vulnerability-alerts
gh api --method PUT repos/{owner}/{repo}/automated-security-fixes
jq '{security_and_analysis}' .github/repo-rules/security-settings.json \
  | gh api --method PATCH repos/{owner}/{repo} --input -
```

(`gh api --method PUT .../rulesets` here is shorthand. Creating and/or updating an existing
ruleset by name actually needs a `GET` first to find its `id`; the `apply-rules` job in
`repo-setup.yml` handles that lookup for you)

### Things that can't / shouldn't be scripted

These require an interactive UI or aren't exposed over the GH REST API:

- **GitHub Advanced Security billing on a private repo:** the `security_and_analysis` PATCH in
  `security-settings.json` requests `advanced_security`/`secret_scanning`/`code scanning` the
  same way the UI toggle does, but if the repo is **private** and the plan/org has no [GHAS license](https://docs.github.com/en/billing/concepts/product-billing/github-advanced-security),
  GH rejects it (`apply-rules` logs a `::warning::` instead of failing).
- **Repository visibility (public/private) and repository deletion protections:** visibility
  can be scripted (`PATCH /repos/{owner}/{repo}` with `"private": true|false`), but changing
  it is disruptive enough that this template deliberately leaves it as a manual, deliberate
  choice at repo-creation time instead of something `repo-setup.yml` flips silently.
- **Limiting how many branches/tags can be updated in a single push:** (Settings -> General ->
  Pushes) this is a GitHub Preview feature with no documented, stable REST field as
  of this writing, so there's nothing for `repo-setup.yml` to call. Set it manually in the UI if you want it.
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
