#!/usr/bin/env python3
"""Print the release note for one version, taken from CHANGELOG.md.

    python3 scripts/release_notes.py <version> [--changelog CHANGELOG.md]

The note is the CHANGELOG's opening lines, which tell Claude Code users how to
update, followed by the section for that version only. The release workflow
writes it into the draft release, so the draft is ready to publish as it is.
Fails when the CHANGELOG has no section for the version.
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def release_notes(changelog: str, version: str) -> str:
    lines = changelog.splitlines()
    starts = [i for i, line in enumerate(lines) if line.startswith("## ")]
    if not starts:
        raise SystemExit("The CHANGELOG has no version sections.")

    intro = [line for line in lines[: starts[0]] if not line.startswith("# ")]
    heading = f"## {version}"
    for n, start in enumerate(starts):
        if lines[start] == heading or lines[start].startswith(f"{heading} "):
            end = starts[n + 1] if n + 1 < len(starts) else len(lines)
            section = lines[start:end]
            break
    else:
        raise SystemExit(
            f"The CHANGELOG has no section for {version}. Add '## {version} (date)'."
        )

    return "\n".join(intro).strip() + "\n\n" + "\n".join(section).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("version", help="such as 0.1.3, without the v")
    parser.add_argument("--changelog", type=Path, default=ROOT / "CHANGELOG.md")
    args = parser.parse_args()

    sys.stdout.write(release_notes(args.changelog.read_text(), args.version))


if __name__ == "__main__":
    sys.exit(main())
