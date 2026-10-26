#!/usr/bin/env python3
"""Fail when the plugin folder changed since a base branch but its version did not go up.

    python3 scripts/check_version.py <base>

Claude shows customers an update only when the plugin's version changes, so
every change inside plugins/onyxia must raise the version in its plugin.json.
The check compares the current commit with where it left <base>, such as
origin/develop. A version that has no release tag (v<version>) has not reached
customers yet, so changes to it need no new version.
"""

from __future__ import annotations

import json
import subprocess
import sys

PLUGIN = "plugins/onyxia"
MANIFEST = f"{PLUGIN}/.claude-plugin/plugin.json"


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True)


def version_at(ref: str) -> str | None:
    shown = git("show", f"{ref}:{MANIFEST}")
    return json.loads(shown.stdout)["version"] if shown.returncode == 0 else None


def parsed(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("-")[0].split("."))


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__.strip().split("\n\n")[1].strip())
    base = sys.argv[1]

    diff = git("diff", "--name-only", f"{base}...HEAD", "--", PLUGIN)
    if diff.returncode:
        raise SystemExit(diff.stderr.strip())
    changed = diff.stdout.split()
    if not changed:
        print("The plugin folder did not change.")
        return 0

    before, after = version_at(base), version_at("HEAD")
    if before is None:
        print(f"The plugin is new on this branch, at version {after}.")
        return 0
    if not git("rev-parse", "-q", "--verify", f"refs/tags/v{before}").stdout:
        print(f"The plugin changed; its version {before} is not released yet.")
        return 0
    if after is not None and parsed(after) > parsed(before):
        print(f"The plugin changed and its version went from {before} to {after}.")
        return 0

    print(
        f"The plugin folder changed but its version is {after}, "
        f"not above {before}. Raise version in {MANIFEST}. Changed files:"
    )
    for path in changed:
        print(f"  {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
