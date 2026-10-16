#!/usr/bin/env python3
"""Build the lightweight Seojae theme from source and its MIT license."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


def render_css(root: Path) -> str:
    source = (root / "src/theme.css").read_text(encoding="utf-8").rstrip() + "\n"
    license_text = (root / "LICENSE").read_text(encoding="utf-8").strip()
    declarations = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    if re.search(r"@font-face|@import|url\s*\(", declarations, re.IGNORECASE):
        raise ValueError("src/theme.css must not load runtime assets; use installed fonts")
    return f'@charset "UTF-8";\n\n/*\n{license_text}\n*/\n\n{source}'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    root = parser.parse_args().root.resolve()
    output = root / "theme.css"
    built = render_css(root)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(built)
    temporary.replace(output)
    print(f"Built {output} ({output.stat().st_size} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
