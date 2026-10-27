"""The version check, seen from outside: a branch's commits against its base branch."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check_version.py"
MANIFEST = Path("plugins/onyxia/.claude-plugin/plugin.json")
# The version the real plugin is at. The fixture tags it as released.
VERSION = json.loads((ROOT / MANIFEST).read_text())["version"]
MAJOR, MINOR, PATCH = (int(part) for part in VERSION.split("."))
HIGHER = f"{MAJOR}.{MINOR}.{PATCH + 1}"


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        [
            "git",
            *("-c", "user.name=Test", "-c", "user.email=test@example.com"),
            *("-c", "commit.gpgsign=false"),
            *args,
        ],
        cwd=repo,
        check=True,
        capture_output=True,
    )


def check(repo: Path, base: str = "base") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK), base],
        cwd=repo,
        capture_output=True,
        text=True,
    )


class VersionCheckTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        shutil.copytree(ROOT / "plugins", self.repo / "plugins")
        (self.repo / "README.md").write_text("Repo.\n")
        git(self.repo, "init", "-q", "-b", "base")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "base")
        git(self.repo, "tag", f"v{VERSION}")
        git(self.repo, "checkout", "-q", "-b", "change")

    def tearDown(self):
        self._tmp.cleanup()

    def commit(self, path: str, text: str) -> None:
        (self.repo / path).write_text(text)
        git(self.repo, "commit", "-q", "-am", f"edit {path}")

    def bump(self, version: str) -> None:
        manifest = json.loads((self.repo / MANIFEST).read_text())
        manifest["version"] = version
        self.commit(str(MANIFEST), json.dumps(manifest, indent=2) + "\n")

    def test_a_plugin_change_without_a_version_change_fails(self):
        self.commit("plugins/onyxia/README.md", "Changed.\n")

        result = check(self.repo)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("plugins/onyxia/README.md", result.stdout + result.stderr)
        self.assertIn(VERSION, result.stdout + result.stderr)

    def test_the_same_change_with_a_version_bump_passes(self):
        self.commit("plugins/onyxia/README.md", "Changed.\n")
        self.bump(HIGHER)

        result = check(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_version_that_goes_down_fails(self):
        self.commit("plugins/onyxia/README.md", "Changed.\n")
        self.bump("0.0.9")

        result = check(self.repo)

        self.assertNotEqual(result.returncode, 0)

    def test_a_version_never_released_can_change_without_a_bump(self):
        git(self.repo, "tag", "-d", f"v{VERSION}")
        self.commit("plugins/onyxia/README.md", "Changed.\n")

        result = check(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not released", result.stdout)

    def test_a_change_outside_the_plugin_needs_no_version_change(self):
        self.commit("README.md", "Changed.\n")

        result = check(self.repo)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
