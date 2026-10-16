#!/usr/bin/env python3
"""Validate the Seojae repository and its release artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from build import render_css


SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
EXPECTED_AUTHOR = "takjakim"
EXPECTED_AUTHOR_URL = "https://github.com/takjakim"
# Project budget, intentionally conservative; not an official directory limit.
MAX_CSS_BYTES = 100_000
REQUIRED_FILES = (
    "README.md",
    "LICENSE",
    "manifest.json",
    "versions.json",
    "theme.css",
    "src/theme.css",
)
TEXT_SUFFIXES = {".css", ".json", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"}
PRIVATE_OR_SECRET_PATTERNS = {
    "macOS private path": re.compile("/" + r"Users/[^/\s]+/"),
    "Linux private path": re.compile("/" + r"home/[^/\s]+/"),
    "Windows private path": re.compile(r"[A-Za-z]:\\\\Users\\\\[^\\\s]+\\\\"),
    "GitHub token": re.compile(r"\b(?:gh[opsu]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "generic API secret": re.compile(r"(?i)\b(?:api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
}


class Validation:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def load_json(self, relative: str) -> object | None:
        try:
            return json.loads((self.root / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            self.error(f"{relative}: cannot read valid JSON: {exc}")
            return None

    def validate_files(self) -> None:
        for relative in REQUIRED_FILES:
            path = self.root / relative
            if not path.is_file() or path.stat().st_size == 0:
                self.error(f"{relative}: required non-empty file is missing")

    def validate_metadata(self) -> None:
        manifest = self.load_json("manifest.json")
        versions = self.load_json("versions.json")
        if not isinstance(manifest, dict) or not isinstance(versions, dict):
            return

        for key in ("name", "version", "minAppVersion", "author", "authorUrl"):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                self.error(f"manifest.json: {key} must be a non-empty string")

        version = manifest.get("version")
        minimum = manifest.get("minAppVersion")
        if isinstance(version, str) and not SEMVER.fullmatch(version):
            self.error("manifest.json: version must be MAJOR.MINOR.PATCH without a v prefix")
        if isinstance(minimum, str) and not SEMVER.fullmatch(minimum):
            self.error("manifest.json: minAppVersion must be MAJOR.MINOR.PATCH")
        if manifest.get("name") != "Seojae":
            self.error("manifest.json: name must be Seojae")
        if manifest.get("author") != EXPECTED_AUTHOR:
            self.error(f"manifest.json: author must be {EXPECTED_AUTHOR}")
        if manifest.get("authorUrl") != EXPECTED_AUTHOR_URL:
            self.error(f"manifest.json: authorUrl must be {EXPECTED_AUTHOR_URL}")

        for listed_version, listed_minimum in versions.items():
            if not isinstance(listed_version, str) or not SEMVER.fullmatch(listed_version):
                self.error(f"versions.json: invalid version key {listed_version!r}")
            if not isinstance(listed_minimum, str) or not SEMVER.fullmatch(listed_minimum):
                self.error(f"versions.json: invalid minimum version for {listed_version!r}")
        if isinstance(version, str) and versions.get(version) != minimum:
            self.error("versions.json: current manifest version must map to minAppVersion")

    def validate_css(self) -> None:
        try:
            css = (self.root / "theme.css").read_text(encoding="utf-8")
            expected = render_css(self.root)
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            self.error(f"CSS build inputs are invalid: {exc}")
            return

        if len(css.encode("utf-8")) > MAX_CSS_BYTES:
            self.error(f"theme.css: exceeds the project size budget of {MAX_CSS_BYTES} bytes")
        declarations = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        if re.search(r"@font-face|@import|url\s*\(", declarations, re.IGNORECASE):
            self.error("theme.css: runtime assets are not allowed; use installed fonts")
        if css != expected:
            self.error("theme.css: generated artifact is stale or modified; rebuild with scripts/build.py")

    def validate_public_text(self) -> None:
        for path in sorted(self.root.rglob("*")):
            if (not path.is_file()
                    or any(part in {".git", ".local", "__pycache__"} for part in path.parts)
                    or path.suffix.lower() not in TEXT_SUFFIXES):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                self.error(f"{path.relative_to(self.root)}: expected UTF-8 text")
                continue
            for label, pattern in PRIVATE_OR_SECRET_PATTERNS.items():
                if pattern.search(text):
                    self.error(f"{path.relative_to(self.root)}: contains a possible {label}")

    def run(self) -> list[str]:
        self.validate_files()
        self.validate_metadata()
        self.validate_css()
        self.validate_public_text()
        return self.errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root (defaults to the parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    errors = Validation(root).run()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    print(f"Validated Seojae {manifest['version']} release artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
