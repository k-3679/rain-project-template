One-time manual setup for this repo. Do these steps in order. Tick items off as you go. Close this issue when done.

## 1. Enable what can't be automated

### Security

Settings → Security → Advanced Security:

- [ ] Dependabot alerts.
- [ ] Dependabot security updates (needs alerts on first).
- [ ] Code scanning. Required for the Trivy and CodeQL SARIF uploads to work.
- [ ] Secret scanning.

### PAT secret

Settings → Secrets and variables → Actions → New repository secret:

- [ ] Add an `ADMIN_TOKEN` secret (**short-lived** fine-grained PAT with *Administration: write* on this repo. Create one if you don't have it). This is required for the **Apply repo rules** workflow to work.

## 2. Edit locally, push once

- [ ] Clone the repo.

### Wire up the languages this project uses

- [ ] [`.github/workflows/validate.yml`](./workflows/validate.yml) → `lint` job: set `if:` and `with.linters:` to the
      same JSON array (e.g. `'["node"]'` or whatever languages your project uses). Both ship empty on purpose so a new repo doesn't
      start with a failing check for a language it doesn't have yet.
- [ ] [Same file](./workflows/validate.yml) → `codeql` job: add `{language, build-mode}` entries to `with.languages:` (set whatever languages your project uses. One entry per language). See
      [CodeQL doc](https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/codeql-code-scanning-for-compiled-languages).
- [ ] [`.github/dependabot.yml`](./dependabot.yml): uncomment the block for your project's package manager(s).

### License and README

- [ ] Add a `LICENSE` if required. The template ships without one.
- [ ] `README.md`: update it to match your project (description, prerequisites, structure, stack, etc.).
- [ ] Commit and push to `main`.

That push runs [**Validate Changes**](./workflows/validate.yml) and generates the Trivy and
CodeQL baselines.

## 3. Apply the repo rules

Run this last. It protects `main`, so direct pushes stop working from here on and everything
goes through a PR.

- [ ] Skim [`.github/repo-rules/README.md`](./repo-rules/README.md) for the things it deliberately doesn't touch.
- [ ] Actions tab → run **Apply repo rules**.
- [ ] Close this issue when done.

> [!WARNING]
> Any later change to `./repo-rules/*.json` needs another run of **Apply repo rules** to take
> effect.

## Adding a required check later

### A new job inside Validate Changes

- [ ] Add the job to [`validate.yml`](./workflows/validate.yml).
- [ ] **Add its job id to `needs:` on the `summary` job.** Without this the job still runs and
      still appears in the PR checks list, but it can't block a merge, and nothing looks wrong.
- [ ] Edit the summary job to display the added job status (env, verdict check, summary table row).

Nothing in `branch-ruleset.main.json` changes and **Apply repo rules** does not need re-running.

### A job in a different workflow

`summary` can only gate jobs in its own workflow, so this needs a ruleset edit.

- [ ] Run the workflow once on `main` and read the job name off the run.
- [ ] Add it as a context in `required_status_checks` in
      [`branch-ruleset.main.json`](./repo-rules/branch-ruleset.main.json).
- [ ] Actions tab → re-run **Apply repo rules**.

> [!NOTE]
> For jobs that call a reusable workflow whose own job also has a `name:`, GitHub posts
> the check as `<calling job> / <inner job>`, not just the calling job's name.

