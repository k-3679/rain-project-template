One-time manual setup for this repo. Do these steps in order. Tick items off as you go. Close this issue when done.

## Enable what bootstrap can't

### Security

Settings → Security → Advanced Security:

- [ ] Dependabot alerts.
- [ ] Dependabot security updates (needs alerts on first).
- [ ] Code scanning required for the Trivy SARIF upload to work.
- [ ] Secret scanning.

### PAT secret

Settings → Secrets and variables → Actions → New repository secret:

- [ ] Add an `ADMIN_TOKEN` secret (**short-lived** fine-grained PAT with *Administration: write* on this repo. Create one if you don't have it). This is required for the **bootstrap workflow** to work.

## Edit locally, push once

- [ ] Clone the repo.

### Wire up the languages this project uses

- [ ] [`.github/workflows/validate.yml`](./workflows/validate.yml) → `lint` job: set `if:` and `with.linters:` to the
      same JSON array (e.g. `'["node"]'` or whatever languages your project uses). Both ship empty on purpose so a new repo doesn't
      start with a failing check for a language it doesn't have yet.
- [ ] [Same file](./workflows/validate.yml) → `codeql` job: add `{language, build-mode}` entries to `with.languages:` (set whatever languages your project uses. One entry per language). See
      [CodeQL doc](https://docs.github.com/en/code-security/code-scanning/creating-an-advanced-setup-for-code-scanning/codeql-code-scanning-for-compiled-languages).
- [ ] [`.github/dependabot.yml`](./dependabot.yml): uncomment the block for your project's package manager(s).

### Make it this project's repo

- [ ] `LICENSE`: copyright holder and year.
- [ ] `CHANGELOG.md`: project name.
- [ ] `CHANGELOG.md`: delete the inherited `[Unreleased]` entries and leave the section empty.
- [ ] `.github/CODEOWNERS`.
- [ ] Replace `README.md` with this project's own.
- [ ] Commit and push to `main`.

That push runs the [**Validate Changes**](./workflows/validate.yml) workflow and generates the Trivy/CodeQL baselines.

> [!NOTE]
> You don't need to touch `required_status_checks` in [`branch-ruleset.main.json`](./repo-rules/branch-ruleset.main.json).
> The single required check is the `Validation summary` job, which needs every other job in the [**Validate Changes**](./workflows/validate.yml)
> workflow.

## Apply the repo rules

- [ ] Skim [`.github/repo-rules/README.md`](./repo-rules/README.md) for the things it deliberately doesn't touch.
- [ ] Actions tab → run **Bootstrap repo settings**.
- [ ] Close this issue when done.

> [!NOTE]
> Any changes you make to `./repo-rules/*.json` afterwards will require a rerun of **Bootstrap repo settings** to apply.

## Adding a required check later
 
### A new job inside Validate Changes
 
- [ ] Add the job to [`validate.yml`](./workflows/validate.yml).
- [ ] **Add its job id to `needs:` on the `summary` job.**
- [ ] Edit the summary job to display the added job status (env, verdict check, summary table row).

Nothing in `branch-ruleset.main.json` changes and bootstrap does not need re-running.
 
### A job in a different workflow
 
`summary` can only gate jobs in its own workflow, so this needs a ruleset edit.
 
- [ ] Run the workflow once on `main` and read the job name off the run.
- [ ] Add it as a context in `required_status_checks` in
      [`branch-ruleset.main.json`](./repo-rules/branch-ruleset.main.json).
- [ ] Actions tab → re-run **Bootstrap repo settings**.

> [!WARNING]
> For jobs that call a reusable workflow whose own job also has a `name:`, GitHub posts
> the check as `<calling job> / <inner job>`, not just the calling job's name. Use the
> "Add checks" search from the ruleset's page (settings → Rulesets → Require status checks to pass → Add checks) to find the real context.

