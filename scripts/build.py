#!/usr/bin/env python3
"""Build the Onyxia plugin for one environment.

    python3 scripts/build.py [target] [--out dist]

A target is a file in targets/, named without its extension (only production
is kept here), or the path to a target file, such as the develop and staging
files in onyxia-agent under claude-plugin/targets/. With no target the build is
production. The build copies plugins/onyxia to <out>/onyxia, writes the
target's server address and sign-in client ID into its .mcp.json, pins the
Claude Code sign-in callback port, and zips the folder as
<out>/onyxia-<target>-<version>.zip for upload to Claude.
"""

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugins" / "onyxia"
TARGETS = ROOT / "targets"
SERVER_FILE = ".mcp.json"
SERVER = "onyxia-cyber"
# Fixes Claude Code's sign-in return address at http://localhost:41871/callback,
# which each Frontegg environment allows.
CALLBACK_PORT = 41871
# Files the operating system leaves behind, never part of the plugin.
IGNORED = (".DS_Store", "__pycache__")
# Zip entries get one fixed time, so the same files always make the same zip.
ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def read_target(name: str) -> dict:
    path = Path(name) if name.endswith(".json") else TARGETS / f"{name}.json"
    if not path.is_file():
        known = ", ".join(sorted(p.stem for p in TARGETS.glob("*.json")))
        raise SystemExit(f"No target '{name}'. Known targets: {known}.")

    target = json.loads(path.read_text())
    for key in ("url", "clientId"):
        if not target.get(key):
            raise SystemExit(f"Target '{name}' has no {key}.")

    return target


def build(name: str, out: Path) -> tuple[Path, Path]:
    target = read_target(name)
    plugin = out / "onyxia"
    if plugin.exists():
        shutil.rmtree(plugin)
    shutil.copytree(SOURCE, plugin, ignore=shutil.ignore_patterns(*IGNORED))

    server_file = plugin / SERVER_FILE
    servers = json.loads(server_file.read_text())
    entry = servers["mcpServers"][SERVER]
    entry["url"] = target["url"]
    entry["oauth"] = {"clientId": target["clientId"], "callbackPort": CALLBACK_PORT}
    server_file.write_text(json.dumps(servers, indent=2) + "\n")

    manifest = json.loads((plugin / ".claude-plugin" / "plugin.json").read_text())
    archive = out / f"onyxia-{Path(name).stem}-{manifest['version']}.zip"
    for stale in out.glob("onyxia-*.zip"):
        stale.unlink()
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zipped:
        for path in sorted(plugin.rglob("*")):
            if path.is_file():
                info = zipfile.ZipInfo(str(path.relative_to(plugin)), ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zipped.writestr(info, path.read_bytes())

    return plugin, archive


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("target", nargs="?", default="production")
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    plugin, archive = build(args.target, args.out)
    print(f"Built {args.target}: {plugin}")
    print(f"Zip for upload: {archive}")


if __name__ == "__main__":
    sys.exit(main())
