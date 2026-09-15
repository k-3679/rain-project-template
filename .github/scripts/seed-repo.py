#!/usr/bin/env python3
"""Seed a repo created from rain-project-template.

Rewrites README.md, .github/CODEOWNERS and CHANGELOG.md with this repo's own
values. Run once by .github/workflows/initialize-repo.yml, which then deletes
this script along with itself.
"""

import os
import re
import subprocess
import sys


REMOVED = (
    ".github/workflows/init-repo.yml",
    ".github/scripts/",
    ".github/SETUP.md",
)

BRANCHING = """## Branching & release flow

This repo follows **GitHub Flow**: `main` is always deployable, every change lands
through a short-lived branch and a PR, no `develop` branch, no long-lived release
branches.

- Branch off `main`, commit, open a PR.
- PR needs 1 approval, resolved review threads, and a passing `Validation summary`
  check before it can merge (`branch-ruleset.main.json`).
- **Squash merge only:** one commit per PR, linear `main` history, one changelog
  entry (`Unreleased`) to match the squashed commit (`repo-settings.json`). Every
  merged commit in `main` is a ready to release (revertible) feature.
- Feature branch is deleted automatically on merge.
- Tag a release straight off `main`. `tag-ruleset.releases.json` locks that tag from
  being moved or deleted afterwards.

See [`.github/repo-rules/README.md`](.github/repo-rules/README.md#why) for the full
reasoning behind each rule this enforces.
"""


# Every tracked path, minus the ones being deleted in this same commit
def tracked_files():
    try:
        out = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        ).stdout
        paths = out.splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        paths = []
        for root, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                paths.append(os.path.relpath(os.path.join(root, f), ".").replace(os.sep, "/"))

    return sorted(
        p for p in paths if not any(p == r or p.startswith(r) for r in REMOVED)
    )


def build_tree(paths):
    tree = {}
    for path in paths:
        node = tree
        parts = path.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None
    return tree


def render_tree(node, prefix=""):
    files = sorted(k for k, v in node.items() if v is None)
    dirs = sorted(k for k, v in node.items() if v is not None)
    entries = [(f, None) for f in files] + [(d, node[d]) for d in dirs]

    lines = []
    for i, (name, child) in enumerate(entries):
        last = i == len(entries) - 1
        lines.append(f"{prefix}{'└── ' if last else '├── '}{name}{'/' if child else ''}")
        if child:
            lines.extend(render_tree(child, prefix + ("    " if last else "│   ")))
    return lines


def architecture(name):
    tree = "\n".join(render_tree(build_tree(tracked_files())))
    return f"## Project structure\n\n```\n{name}/\n{tree}\n```\n"


def badges(owner, name):
    base = f"https://github.com/{owner}/{name}"
    return (
        f"[![Apply repo rules]({base}/actions/workflows/apply-repo-rules.yml/badge.svg)]"
        f"({base}/actions/workflows/apply-repo-rules.yml)\n"
        f"[![Validate Changes]({base}/actions/workflows/validate.yml/badge.svg)]"
        f"({base}/actions/workflows/validate.yml)\n"
        f"[![Changelog](https://img.shields.io/badge/changelog-CHANGELOG.md-blue)](CHANGELOG.md)\n"
        f"[![Release](https://img.shields.io/github/v/release/{owner}/{name}"
        f"?label=release&sort=semver)]({base}/releases)\n"
    )


def readme(owner, name, desc, issue):
    parts = [f"# {name}\n", badges(owner, name)]
    if desc:
        parts.append(f"{desc}\n")
    checklist = (
        f"[**📝 Repo setup checklist**]({issue})" if issue
        else "**📝 Repo setup checklist** issue"
    )
    parts.append(
        "## TODO\n\n"
        f"- Open the {checklist} and follow the provided instructions.\n"
    )
    parts.append(architecture(name))
    parts.append(BRANCHING)
    parts.append(
        "## Security\n\n"
        "Do not open a public issue for a vulnerability. See\n"
        "[SECURITY.md](.github/SECURITY.md) for how to report one.\n"
    )

    return "\n".join(parts)


def main() -> int:
    try:
        name = os.environ["REPO_NAME"]
        owner = os.environ["OWNER"]
    except KeyError as missing:
        print(f"::error::missing environment variable {missing}", file=sys.stderr)
        return 1

    desc = os.environ.get("REPO_DESC", "").strip()
    issue = os.environ.get("ISSUE_URL", "").strip()

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme(owner, name, desc, issue))

    with open(".github/CODEOWNERS", "w", encoding="utf-8") as f:
        f.write(f"*   @{owner}\n")

    with open("CHANGELOG.md", encoding="utf-8") as f:
        changelog = f.read()
    changelog = re.sub(
        # find the [Unreleased] section (heading + body) and replace it with the heading only (## \[Unreleased\]\n)
        r"(## \[Unreleased\]\n).*?(?=\n## |\Z)", r"\1", changelog, flags=re.S
    )
    with open("CHANGELOG.md", "w", encoding="utf-8") as f:
        f.write(changelog.rstrip() + "\n")

    print(f"Seeded README.md, .github/CODEOWNERS and CHANGELOG.md for {owner}/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
