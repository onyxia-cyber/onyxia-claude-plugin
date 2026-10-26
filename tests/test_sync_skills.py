"""The skills sync and drift check, seen from outside: the files it writes and what it reports."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYNC = ROOT / "scripts" / "sync_skills.py"
PLUGIN = ROOT / "plugins" / "onyxia"
SKILLS = ("inventory", "lookup", "metrics")
# CI clones onyxia-agent at main and names it here; locally a sibling checkout works.
AGENT = Path(os.environ.get("ONYXIA_AGENT", ROOT.parent / "onyxia-agent"))


def sync(agent: Path, plugin: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SYNC), str(agent), "--plugin", str(plugin), *options],
        capture_output=True,
        text=True,
    )


def files(folder: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(folder)): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file()
    }


def fake_agent(root: Path) -> Path:
    """An onyxia-agent checkout with the three skills, Python files and a cache."""
    skills = root / "app" / "nexa" / "skills"
    for name in SKILLS:
        (skills / name).mkdir(parents=True)
        (skills / name / "SKILL.md").write_text(f"---\nname: {name}\n---\n{name}\n")
    (skills / "inventory" / "references").mkdir()
    (skills / "inventory" / "references" / "devices.md").write_text("Devices.\n")
    (skills / "registry.py").write_text("# loader\n")
    (skills / "inventory" / "__pycache__").mkdir()
    (skills / "inventory" / "__pycache__" / "x.pyc").write_bytes(b"\0")
    (skills / "inventory" / "helper.py").write_text("# helper\n")
    return root


class SyncTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.agent = fake_agent(self.tmp / "agent")
        self.plugin = self.tmp / "plugin"
        self.plugin.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_sync_copies_the_three_skills_without_python_files_or_caches(self):
        result = sync(self.agent, self.plugin)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            set(files(self.plugin / "skills")),
            {
                "inventory/SKILL.md",
                "inventory/references/devices.md",
                "lookup/SKILL.md",
                "metrics/SKILL.md",
            },
        )
        self.assertIn("inventory/SKILL.md", result.stdout)

    def test_a_second_sync_reports_no_changes(self):
        sync(self.agent, self.plugin)

        result = sync(self.agent, self.plugin)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No changes", result.stdout)

    def test_sync_names_changed_and_removed_files_and_removes_them(self):
        sync(self.agent, self.plugin)
        skills = self.agent / "app" / "nexa" / "skills"
        (skills / "lookup" / "SKILL.md").write_text("changed\n")
        (skills / "inventory" / "references" / "devices.md").unlink()

        result = sync(self.agent, self.plugin)

        self.assertIn("changed: lookup/SKILL.md", result.stdout)
        self.assertIn("removed: inventory/references/devices.md", result.stdout)
        self.assertFalse(
            (self.plugin / "skills" / "inventory" / "references" / "devices.md").exists()
        )

    def test_the_check_fails_and_names_a_file_that_differs_by_one_character(self):
        sync(self.agent, self.plugin)
        copied = self.plugin / "skills" / "metrics" / "SKILL.md"
        copied.write_text(copied.read_text().replace("metrics\n", "metricz\n", 1))

        result = sync(self.agent, self.plugin, "--check")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metrics/SKILL.md", result.stdout + result.stderr)
        self.assertIn("metricz", copied.read_text())

    def test_the_check_names_a_file_only_the_plugin_has(self):
        sync(self.agent, self.plugin)
        (self.plugin / "skills" / "lookup" / "extra.md").write_text("extra\n")

        result = sync(self.agent, self.plugin, "--check")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("lookup/extra.md", result.stdout + result.stderr)

    def test_the_check_passes_when_the_skills_match(self):
        sync(self.agent, self.plugin)

        result = sync(self.agent, self.plugin, "--check")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_folder_that_is_not_an_onyxia_agent_checkout_is_refused(self):
        result = sync(self.tmp / "nowhere", self.plugin)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("onyxia-agent", result.stderr)


class PluginSkillsTests(unittest.TestCase):
    @unittest.skipUnless(
        (AGENT / "app" / "nexa" / "skills").is_dir() or os.environ.get("CI"),
        "no onyxia-agent checkout; set ONYXIA_AGENT to one",
    )
    def test_the_plugin_skills_match_onyxia_agent_byte_for_byte(self):
        result = sync(AGENT, PLUGIN, "--check")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_plugin_has_exactly_the_three_skills(self):
        self.assertEqual(
            sorted(path.parent.name for path in (PLUGIN / "skills").glob("*/SKILL.md")),
            list(SKILLS),
        )


if __name__ == "__main__":
    unittest.main()
