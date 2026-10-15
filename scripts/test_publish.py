#!/usr/bin/env python3
"""Safety tests for the GitHub release publisher using local command doubles."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REAL_GIT = shutil.which("git")


FAKE_GIT = r'''#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
with Path(os.environ["MOCK_LOG"]).open("a", encoding="utf-8") as log:
    log.write("git " + " ".join(args) + "\n")

if "ls-remote" in args:
    main = os.environ.get("MOCK_REMOTE_MAIN", "")
    tag = os.environ.get("MOCK_REMOTE_TAG", "")
    other = os.environ.get("MOCK_OTHER_HEAD", "")
    if main:
        print(f"{main}\trefs/heads/main")
    if other:
        print(f"{other}\trefs/heads/trunk")
    if tag:
        print(f"{tag}\trefs/tags/{os.environ['MOCK_VERSION']}")
    raise SystemExit(0)
if "fetch" in args or "push" in args:
    raise SystemExit(0)
if "merge-base" in args:
    raise SystemExit(0 if os.environ.get("MOCK_REMOTE_ANCESTOR", "1") == "1" else 1)
os.execv(os.environ["REAL_GIT"], [os.environ["REAL_GIT"], *args])
'''


FAKE_GH = r'''#!/usr/bin/env python3
import json, os, shutil, subprocess, sys
from pathlib import Path

args = sys.argv[1:]
with Path(os.environ["MOCK_LOG"]).open("a", encoding="utf-8") as log:
    log.write("gh " + " ".join(args) + "\n")

if args[:2] == ["auth", "status"]:
    raise SystemExit(0 if os.environ.get("MOCK_AUTH", "1") == "1" else 1)
if args[:2] == ["api", "user"]:
    print(os.environ.get("MOCK_OWNER", "takjakim"))
    raise SystemExit(0)
if args[:1] == ["api"] and "/releases/tags/" in args[1]:
    state = os.environ.get("MOCK_RELEASE", "missing")
    if state == "missing":
        print("gh: Not Found (HTTP 404)", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({"tag_name": os.environ["MOCK_VERSION"], "draft": state == "draft", "prerelease": state == "prerelease"}))
    raise SystemExit(0)
if args[:1] == ["api"] and args[1].startswith("repos/"):
    if os.environ.get("MOCK_REPOSITORY", "1") == "1":
        print(json.dumps({"private": False}))
        raise SystemExit(0)
    print("gh: Not Found (HTTP 404)", file=sys.stderr)
    raise SystemExit(1)
if args[:2] == ["repo", "create"]:
    if "--remote" in args:
        root = args[args.index("--source") + 1]
        subprocess.run([os.environ["REAL_GIT"], "-C", root, "remote", "add", "origin", "https://github.com/takjakim/obsidian-seojae.git"], check=True)
    raise SystemExit(0)
if args[:2] == ["release", "create"]:
    Path(os.environ["MOCK_RELEASE_MARKER"]).write_text("created", encoding="utf-8")
    raise SystemExit(0)
if args[:2] == ["release", "download"]:
    destination = Path(args[args.index("--dir") + 1])
    destination.mkdir(parents=True, exist_ok=True)
    root = Path(os.environ["MOCK_ROOT"])
    shutil.copy2(root / "theme.css", destination / "theme.css")
    shutil.copy2(root / "manifest.json", destination / "manifest.json")
    raise SystemExit(0)
raise SystemExit(f"unexpected gh invocation: {args}")
'''


class PublishSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        if REAL_GIT is None:
            self.skipTest("git is unavailable")
        self.temporary = tempfile.TemporaryDirectory(prefix="seojae-publish-test-")
        self.base = Path(self.temporary.name)
        self.repository = self.base / "repository"
        shutil.copytree(ROOT, self.repository, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self._write_executable(self.bin / "git", FAKE_GIT)
        self._write_executable(self.bin / "gh", FAKE_GH)
        self.log = self.base / "commands.log"
        self.release_marker = self.base / "release-created"
        self._git("init", "-b", "main")
        self._git("config", "user.name", "Release Test")
        self._git("config", "user.email", "release-test@example.invalid")
        self._git("add", "-A")
        self._git("commit", "-m", "test release")
        self.head = self._git("rev-parse", "HEAD").stdout.strip()
        self.version = json.loads((self.repository / "manifest.json").read_text(encoding="utf-8"))["version"]

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_executable(self, path: Path, content: str) -> None:
        path.write_text(textwrap.dedent(content), encoding="utf-8")
        path.chmod(0o755)

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [REAL_GIT, "-C", self.repository, *args],
            check=True,
            text=True,
            capture_output=True,
        )

    def environment(self, **overrides: str) -> dict[str, str]:
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{self.bin}{os.pathsep}{environment['PATH']}",
                "REAL_GIT": REAL_GIT,
                "MOCK_LOG": str(self.log),
                "MOCK_ROOT": str(self.repository),
                "MOCK_VERSION": self.version,
                "MOCK_RELEASE_MARKER": str(self.release_marker),
                "MOCK_AUTH": "1",
                "MOCK_OWNER": "takjakim",
                "MOCK_REPOSITORY": "1",
                "MOCK_RELEASE": "missing",
                "MOCK_REMOTE_MAIN": "",
                "MOCK_REMOTE_TAG": "",
                "MOCK_OTHER_HEAD": "",
                "MOCK_REMOTE_ANCESTOR": "1",
            }
        )
        environment.update(overrides)
        return environment

    def publish(self, **overrides: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["sh", "scripts/publish.sh"],
            cwd=self.repository,
            env=self.environment(**overrides),
            text=True,
            capture_output=True,
        )

    def command_log(self) -> str:
        return self.log.read_text(encoding="utf-8") if self.log.exists() else ""

    def test_auth_failure_stops_before_any_remote_mutation(self) -> None:
        result = self.publish(MOCK_AUTH="0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("authentication or connectivity", result.stderr)
        self.assertNotIn("gh repo create", self.command_log())
        self.assertNotIn("git push", self.command_log())
        self.assertEqual(self._git("tag", "--list").stdout, "")

    def test_existing_remote_ancestor_publishes_without_duplicate_origin(self) -> None:
        result = self.publish(MOCK_REMOTE_MAIN=self.head)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Published and verified", result.stdout)
        self.assertTrue(self.release_marker.exists())
        self.assertEqual(self._git("remote", "get-url", "origin").stdout.strip(), "https://github.com/takjakim/obsidian-seojae.git")
        self.assertEqual(self.command_log().count("remote add origin"), 1)
        self.assertEqual(self._git("tag", "--list", self.version).stdout.strip(), self.version)

    def test_new_repository_with_preconfigured_origin_does_not_add_it_again(self) -> None:
        self._git("remote", "add", "origin", "https://github.com/takjakim/obsidian-seojae.git")
        result = self.publish(MOCK_REPOSITORY="0")
        self.assertEqual(result.returncode, 0, result.stderr)
        create_calls = [line for line in self.command_log().splitlines() if line.startswith("gh repo create")]
        self.assertEqual(len(create_calls), 1)
        self.assertNotIn("--remote", create_calls[0])
        self.assertNotIn("--source", create_calls[0])
        self.assertTrue(self.release_marker.exists())

    def test_mismatched_remote_tag_stops_before_push(self) -> None:
        self._git("remote", "add", "origin", "https://github.com/takjakim/obsidian-seojae.git")
        result = self.publish(MOCK_REMOTE_TAG="0" * 40)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("different commit", result.stderr)
        self.assertNotIn("git push", self.command_log())
        self.assertFalse(self.release_marker.exists())

    def test_draft_and_prerelease_are_not_reported_as_published(self) -> None:
        self._git("remote", "add", "origin", "https://github.com/takjakim/obsidian-seojae.git")
        for release_state in ("draft", "prerelease"):
            with self.subTest(release_state=release_state):
                self.log.write_text("", encoding="utf-8")
                result = self.publish(MOCK_REMOTE_TAG=self.head, MOCK_RELEASE=release_state)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(release_state, result.stderr)
                self.assertNotIn("git push", self.command_log())
                self.assertFalse(self.release_marker.exists())


if __name__ == "__main__":
    unittest.main()
