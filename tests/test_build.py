"""The built plugin folder, seen from outside: what the build script writes for a target."""

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "scripts" / "build.py"
SOURCE = ROOT / "plugins" / "onyxia"
TARGETS = sorted(path.stem for path in (ROOT / "targets").glob("*.json"))
# A made-up environment. The real develop and staging targets live in onyxia-agent,
# out of this public repository, and are built by path the same way.
EXAMPLE = {"url": "https://example.test/mcp", "clientId": "00000000-0000-0000-0000-000000000000"}
SERVER_FILE = ".mcp.json"
CALLBACK_PORT = 41871


def build(out: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(BUILD), "--out", str(out), *args],
        capture_output=True,
        text=True,
    )


def files(folder: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(folder)): path.read_bytes()
        for path in sorted(folder.rglob("*"))
        if path.is_file() and path.name != ".DS_Store"
    }


def server(folder: Path) -> dict:
    return json.loads((folder / SERVER_FILE).read_text())["mcpServers"]["onyxia"]


def target(name: str) -> dict:
    if name == "example":
        return EXAMPLE
    return json.loads((ROOT / "targets" / f"{name}.json").read_text())


def validate(path: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["claude", "plugin", "validate", *options, str(path)],
        capture_output=True,
        text=True,
    )


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._out = tempfile.TemporaryDirectory()
        cls.out = Path(cls._out.name)
        example = cls.out / "example.json"
        example.write_text(json.dumps(EXAMPLE))
        cls.built: dict[str, Path] = {}
        for name, arg in (("production", "production"), ("example", str(example))):
            result = build(cls.out / name, arg)
            if result.returncode:
                raise AssertionError(f"build {name} failed:\n{result.stderr}")
            cls.built[name] = cls.out / name / "onyxia"

    @classmethod
    def tearDownClass(cls):
        cls._out.cleanup()

    def test_only_the_production_target_is_in_this_public_repository(self):
        self.assertEqual(TARGETS, ["production"])

    def test_with_no_target_the_build_is_production_and_matches_the_source(self):
        with tempfile.TemporaryDirectory() as out:
            result = build(Path(out))

            self.assertEqual(result.returncode, 0, result.stderr)
            built = Path(out) / "onyxia"
            self.assertEqual(files(built), files(self.built["production"]))
            self.assertEqual(files(built), files(SOURCE))

    def test_the_server_file_carries_the_target_address_and_client_id(self):
        for name in self.built:
            with self.subTest(target=name):
                entry = server(self.built[name])

                self.assertEqual(entry["type"], "http")
                self.assertEqual(entry["url"], target(name)["url"])
                self.assertEqual(entry["oauth"]["clientId"], target(name)["clientId"])
                self.assertEqual(entry["oauth"]["callbackPort"], CALLBACK_PORT)

    def test_targets_differ_only_in_the_address_and_client_id(self):
        production = files(self.built["production"])
        for name in self.built:
            with self.subTest(target=name):
                built = files(self.built[name])
                self.assertEqual(set(built), set(production))
                differ = {path for path in built if built[path] != production[path]}
                self.assertLessEqual(differ, {SERVER_FILE})

                entry, base = server(self.built[name]), server(self.built["production"])
                for value in (entry, base):
                    value.pop("url")
                    value["oauth"].pop("clientId")
                self.assertEqual(entry, base)

    def test_each_target_has_a_zip_to_upload_with_the_built_files(self):
        for name in self.built:
            with self.subTest(target=name):
                zips = list((self.out / name).glob("*.zip"))
                self.assertEqual(len(zips), 1)
                with zipfile.ZipFile(zips[0]) as archive:
                    zipped = {
                        info.filename: archive.read(info)
                        for info in archive.infolist()
                        if not info.is_dir()
                    }
                self.assertEqual(zipped, files(self.built[name]))

    def test_a_target_without_an_address_or_client_id_does_not_build(self):
        for missing in ("url", "clientId"):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as out:
                broken = dict(EXAMPLE)
                del broken[missing]
                path = Path(out) / "broken.json"
                path.write_text(json.dumps(broken))

                result = build(Path(out) / "built", str(path))

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(missing, result.stderr)
                self.assertFalse((Path(out) / "built" / "onyxia").exists())

    def test_an_unknown_target_does_not_build(self):
        with tempfile.TemporaryDirectory() as out:
            result = build(Path(out), "nowhere")

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("nowhere", result.stderr)

    def test_every_skill_uses_only_the_front_matter_keys_claude_ai_accepts(self):
        # claude.ai refuses an upload with any other key; the validator does not check.
        allowed = {
            "name",
            "description",
            "license",
            "compatibility",
            "metadata",
            "allowed-tools",
        }
        skills = sorted(self.built["production"].glob("skills/*/SKILL.md"))
        self.assertTrue(skills)
        for path in skills:
            with self.subTest(skill=path.parent.name):
                front = path.read_text().split("---\n", 2)[1]
                keys = {line.split(":")[0] for line in front.splitlines() if line[:1].isalpha()}
                self.assertLessEqual(keys, allowed)
                self.assertIn("name", keys)
                self.assertIn("description", keys)

    def test_claude_validates_the_marketplace_and_every_built_plugin(self):
        for path in (ROOT, *self.built.values()):
            with self.subTest(path=str(path.relative_to(path.parents[1]))):
                result = validate(path, "--strict")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_built_plugin_has_a_problem_the_plugin_directory_refuses(self):
        # Such as a README under 40 words or no license. Without --strict, so the
        # directory's listing warnings (icon, privacy link) do not fail it yet.
        for name in self.built:
            with self.subTest(target=name):
                result = validate(self.built[name], "--profile", "directory")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
