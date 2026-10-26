#!/usr/bin/env python3
"""Copy the Nexa skills from an onyxia-agent checkout into the plugin.

    python3 scripts/sync_skills.py <onyxia-agent> [--check] [--plugin plugins/onyxia]

onyxia-agent is the one source of the skills. The sync copies the inventory,
lookup and metrics folders byte for byte, without Python files and caches,
removes plugin skill files that onyxia-agent no longer has, and prints each file
it changed. With --check it changes nothing and fails when any file differs,
naming each one. CI runs the check against onyxia-agent's main branch.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ("inventory", "lookup", "metrics")
# Where onyxia-agent keeps the skills, under its checkout.
AGENT_SKILLS = Path("app") / "nexa" / "skills"
# Nexa's loader code and what Python or the operating system leave behind.
IGNORED_NAMES = {"__pycache__", ".DS_Store"}
IGNORED_SUFFIXES = {".py", ".pyc"}


def skill_files(folder: Path, names: tuple[str, ...] | None = None) -> dict[str, bytes]:
    """Each skill file under folder by its path inside it, for the named skills or all."""
    roots = [folder / name for name in names] if names else [folder]
    return {
        path.relative_to(folder).as_posix(): path.read_bytes()
        for root in roots
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not IGNORED_NAMES & set(path.relative_to(folder).parts)
        and path.suffix not in IGNORED_SUFFIXES
    }


def differences(source: dict[str, bytes], copy: dict[str, bytes]) -> list[tuple[str, str]]:
    found = [
        ("added" if path not in copy else "changed", path)
        for path in source
        if source[path] != copy.get(path)
    ]
    found += [("removed", path) for path in copy if path not in source]
    return sorted(found, key=lambda change: change[1])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("agent", type=Path, help="path to an onyxia-agent checkout")
    parser.add_argument("--plugin", type=Path, default=ROOT / "plugins" / "onyxia")
    parser.add_argument(
        "--check", action="store_true", help="change nothing; fail on any difference"
    )
    args = parser.parse_args()

    source_folder = args.agent / AGENT_SKILLS
    for name in SKILLS:
        if not (source_folder / name / "SKILL.md").is_file():
            raise SystemExit(
                f"{args.agent} is not an onyxia-agent checkout: "
                f"{AGENT_SKILLS / name / 'SKILL.md'} is missing."
            )

    copy_folder = args.plugin / "skills"
    source = skill_files(source_folder, SKILLS)
    copy = skill_files(copy_folder) if copy_folder.is_dir() else {}
    changes = differences(source, copy)

    if not changes:
        print("No changes: the plugin skills match onyxia-agent.")
        return 0

    if args.check:
        print("The plugin skills differ from onyxia-agent. Run scripts/sync_skills.py.")
        for change, path in changes:
            print(f"  {change}: {path}")
        return 1

    for change, path in changes:
        target = copy_folder / path
        if change == "removed":
            target.unlink()
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source[path])
        print(f"{change}: {path}")

    for folder in sorted(copy_folder.rglob("*"), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()

    return 0


if __name__ == "__main__":
    sys.exit(main())
