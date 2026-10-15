#!/usr/bin/env python3
"""Build theme.css with the approved original Nanum Myeongjo fonts embedded."""

from __future__ import annotations

import argparse
import base64
import hashlib
import re
import tempfile
from pathlib import Path

from validate import EXPECTED_FONT_HASHES, FONT_DATA, FONT_FACE


def load_fonts_from_css(path: Path) -> dict[str, bytes]:
    css = path.read_text(encoding="utf-8")
    fonts: dict[str, bytes] = {}
    for face in FONT_FACE.finditer(css):
        match = FONT_DATA.search(face.group("body"))
        if match:
            fonts[match.group("weight")] = base64.b64decode(match.group("data"), validate=True)
    return fonts


def load_fonts_from_directory(path: Path) -> dict[str, bytes]:
    fonts: dict[str, bytes] = {}
    expected_by_hash = {digest: weight for weight, digest in EXPECTED_FONT_HASHES.items()}
    for candidate in path.glob("*.ttf"):
        data = candidate.read_bytes()
        weight = expected_by_hash.get(hashlib.sha256(data).hexdigest())
        if weight:
            fonts[weight] = data
    return fonts


def validate_fonts(fonts: dict[str, bytes]) -> None:
    actual = {weight: hashlib.sha256(data).hexdigest() for weight, data in fonts.items()}
    if actual != EXPECTED_FONT_HASHES:
        raise SystemExit(
            "Font files do not match the approved original Nanum Myeongjo files.\n"
            f"Expected: {EXPECTED_FONT_HASHES}\nActual:   {actual}"
        )


def font_face(weight: str, data: bytes) -> str:
    local_name = "NanumMyeongjo" if weight == "400" else "NanumMyeongjoBold"
    encoded = base64.b64encode(data).decode("ascii")
    return (
        '@font-face {\n'
        '  font-family: "Seojae Myeongjo";\n'
        '  font-style: normal;\n'
        f'  font-weight: {weight};\n'
        '  font-display: swap;\n'
        f'  src: local("{local_name}"), url("data:font/ttf;base64,{encoded}") format("truetype");\n'
        '}\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument(
        "--fonts",
        type=Path,
        help="optional directory containing the two original .ttf files; hashes must match",
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output = root / "theme.css"
    source = (root / "src/theme.css").read_text(encoding="utf-8").rstrip() + "\n"
    license_text = (root / "LICENSE").read_text(encoding="utf-8").strip()
    font_license = (root / "FONT-LICENSE.txt").read_text(encoding="utf-8").rstrip("\n")

    if "@font-face" in source or re.search(r"url\(\s*['\"]?https?://", source, re.IGNORECASE):
        raise SystemExit("src/theme.css must not embed fonts or load remote runtime assets")
    if "SIL OPEN FONT LICENSE" not in font_license or "NHN Corporation" not in font_license:
        raise SystemExit("FONT-LICENSE.txt is not the expected Nanum Myeongjo OFL license")

    fonts = load_fonts_from_directory(args.fonts.resolve()) if args.fonts else load_fonts_from_css(output)
    validate_fonts(fonts)

    built = (
        '@charset "UTF-8";\n\n'
        f"/*\n{license_text}\n\n*/\n\n"
        f"{source}\n\n"
        "/*\nBundled original Nanum Myeongjo fonts, without modification.\n"
        "Source: https://github.com/google/fonts/tree/main/ofl/nanummyeongjo\n"
        f"{font_license}\n\n*/\n\n\n"
        f"{font_face('400', fonts['400'])}\n\n"
        f"{font_face('700', fonts['700'])}"
    )

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=root, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(built)
    temporary.replace(output)
    print(f"Built {output} ({output.stat().st_size} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
