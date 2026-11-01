"""The release note script, seen from outside: a CHANGELOG in, one version's note out."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "release_notes.py"

CHANGELOG = """# Changes

Claude Code users: run the update commands.

```bash
claude plugin update onyxia@onyxia
```

## 0.2.0 (2026-12-01)

- The newest change.

## 0.1.1 (2026-11-01)

- A middle change.

## 0.1.0 (2026-10-01)

The first release.
"""


def notes(version: str, changelog: str = CHANGELOG) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "CHANGELOG.md"
        path.write_text(changelog)
        return subprocess.run(
            [sys.executable, str(SCRIPT), version, "--changelog", str(path)],
            capture_output=True,
            text=True,
        )


class ReleaseNotesTests(unittest.TestCase):
    def test_the_note_has_the_update_lines_and_only_its_own_section(self):
        result = notes("0.1.1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "Claude Code users: run the update commands.\n\n"
            "```bash\nclaude plugin update onyxia@onyxia\n```\n\n"
            "## 0.1.1 (2026-11-01)\n\n- A middle change.\n",
        )

    def test_the_last_section_runs_to_the_end(self):
        result = notes("0.1.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.endswith("## 0.1.0 (2026-10-01)\n\nThe first release.\n"))

    def test_a_version_is_not_matched_by_its_prefix(self):
        result = notes("0.1")
        self.assertNotEqual(result.returncode, 0)

    def test_a_version_with_no_section_fails_and_says_what_to_add(self):
        result = notes("9.9.9")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("## 9.9.9 (date)", result.stderr)

    def test_the_real_changelog_has_a_note_for_the_plugin_version(self):
        version = json.loads(
            (ROOT / "plugins/onyxia/.claude-plugin/plugin.json").read_text()
        )["version"]
        result = subprocess.run(
            [sys.executable, str(SCRIPT), version],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"## {version} ", result.stdout)


if __name__ == "__main__":
    unittest.main()
