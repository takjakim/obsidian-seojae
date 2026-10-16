"""Regression checks for the font-free community release package."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import Validation

ROOT = Path(__file__).resolve().parent.parent


class ReleaseArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="seojae-build-test-")
        self.root = Path(self.temporary.name) / "theme"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", ".local", "__pycache__"))

    def tearDown(self):
        self.temporary.cleanup()

    def test_clean_build_needs_no_previous_css_or_fonts(self):
        expected = (self.root / "theme.css").read_bytes()
        (self.root / "theme.css").unlink()
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/build.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / "theme.css").read_bytes(), expected)
        self.assertEqual(Validation(self.root).run(), [])

    def test_size_regression_is_rejected(self):
        with (self.root / "theme.css").open("a") as file:
            file.write("/*" + "x" * 100_000 + "*/")
        self.assertTrue(any("size budget" in e for e in Validation(self.root).run()))

    def test_bundled_and_remote_fonts_are_rejected(self):
        original = (self.root / "theme.css").read_text()
        for target in ("data:font/ttf;base64,AAAA", "https://example.invalid/font.woff2"):
            with self.subTest(target=target):
                (self.root / "theme.css").write_text(
                    original + f'\n@font-face {{ font-family: Test; src: url("{target}"); }}\n'
                )
                self.assertTrue(any("runtime assets" in e for e in Validation(self.root).run()))

    def test_stale_generated_css_is_rejected(self):
        with (self.root / "src/theme.css").open("a") as file:
            file.write("\nbody { --file-line-width: 700px; }\n")
        self.assertTrue(any("rebuild" in e for e in Validation(self.root).run()))


if __name__ == "__main__":
    unittest.main()
