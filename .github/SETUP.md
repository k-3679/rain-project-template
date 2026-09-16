One-time manual setup for this repo. Do these steps in order. Tick items off as you go. Close this issue when done.

## 1. Enable what can't be automated

Settings → Secrets and variables → Actions → New repository secret:

- [ ] Add an `ADMIN_TOKEN` secret (**short-lived** fine-grained PAT with *Administration: write* on this repo. Create one if you don't have it). This is required for the [**Setup repo**](/.github/workflows/repo-setup.yml) workflow to work.

## 2. Run `Setup repo`

Direct pushes to `main` stop working from here on and everything goes through a PR.

- [ ] Read [`.github/repo-rules/README.md`](/.github/repo-rules/README.md) for the things it deliberately doesn't touch.
- [ ] Actions tab → run [**Setup repo**](/.github/workflows/repo-setup.yml), checking the box for each language this project uses (only languages supported by both the linter and CodeQL show up as inputs: Python, Node, Go, Rust, C/C++).

> [!WARNING]
> Any later change to `./repo-rules/*.json` needs another run of **Setup repo** to take
> effect. Once `main` is protected, changing languages later means editing
> `validate.yml`/`dependabot.yml` through a PR instead of re-running `wire-languages`.

## 3. Edit locally, push once

- [ ] Clone the repo.
- [ ] Create a new branch.
- [ ] Add a `LICENSE` if required. The template doesn't include one.
- [ ] Update `README.md` to match your project (description, prerequisites, structure, stack, etc).
- [ ] Update `CHANGELOG.md` to reflect your changes.
- [ ] Commit and push your **local branch**.
- [ ] Create a PR to `main`, wait for the [required checks to pass](/.github/workflows/validate.yml), and merge.

---

- [ ] **Close this issue when done.**

<details>
<summary>🔧 <b>Reference:</b> adding a required check later (not part of first-time setup)</summary>

### A new job inside `Validate Changes` workflow

- [ ] Add the job to [`validate.yml`](/.github/workflows/validate.yml).
- [ ] **Add its job id to `needs:` on the `summary` job.** Without this the job still runs and still appears in the PR checks list, but it can't block a merge, and nothing looks wrong.
- [ ] Edit the summary job to display the added job status (env, verdict check, summary table row).

Nothing in `branch-ruleset.main.json` changes and **Setup repo** does not need re-running.

### A job in a different workflow

[`validate.yml`](/.github/workflows/validate.yml) can only gate jobs in its own workflow, so this needs a ruleset edit.

- [ ] Add the job name as a context in `required_status_checks` in [`branch-ruleset.main.json`](/.github/repo-rules/branch-ruleset.main.json).
- [ ] Actions tab → re-run **Setup repo** (it will skip the `wire-languages` job and re-apply `apply-rules`).

> [!NOTE]
> For jobs that call a reusable workflow whose own job also has a `name:`, GitHub posts
> the check as `<calling job> / <inner job>`, not just the calling job's name.

</details>
