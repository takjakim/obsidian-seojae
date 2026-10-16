# Verification record — 1.1.1

Version 1.1.1 removes all embedded font data from the package. Its `theme.css` is 16,679 bytes, down from 8,199,325 bytes in 1.1.0. The source uses only installed Times New Roman, Nanum Myeongjo/나눔명조, Noto Serif CJK KR and the generic serif fallback; it contains no font download or runtime asset reference.

The validator enforces a conservative 100,000-byte project budget and rejects `@font-face`, `@import` and `url(...)` runtime assets. This budget is a repository safeguard, not an official Obsidian limit. CI also runs regression tests for the build and release safeguards.

## 1.1.1 checks — 2026-10-16

- Build and repository validation passed; all 9 build/publisher regression tests passed.
- A fresh browser fixture using the installed Obsidian 1.14.4 base CSS rendered light/dark layouts and a 390px narrow layout without page-wide horizontal overflow.
- Browser platform-font inspection confirmed local NanumMyeongjo and TimesNewRomanPSMT (`isCustomFont: false`); the release CSS contains no embedded or remote font source.
- Reference paragraphs retained a -36px first-line indent with 36px padding. Quotes and footnotes remained unindented.
- Print-media emulation retained 11pt text, 1.8 line height and heading break avoidance. This is not a native Obsidian PDF-export test.

## Historical preview record — 1.1.0

The visual checks below were recorded on 2026-10-15 using a browser fixture with the locally installed Obsidian 1.13.7 base CSS. That proprietary base CSS is not included in this repository. Removing the embedded fonts in 1.1.1 does not make these checks fresh native-app verification.

## Recorded preview checks

- CSS parsing reported no top-level syntax errors. Style Settings declarations parsed successfully.
- Actual rendered glyphs were NanumMyeongjo, NanumMyeongjoBold, TimesNewRomanPSMT and TimesNewRomanPS-BoldMT; code used Menlo.
- The 1.1.0 embedded font data matched the original font SHA-256 values, including when local-font sources were disabled in the fixture. Version 1.1.1 intentionally removes that data and requires locally installed fonts.
- Text contrast combinations exceeded 4.5:1 in the tested light/dark surfaces.
- Reading density, custom line/paragraph spacing, footnote scale, readable width and user text-size precedence behaved as documented.
- 320px and 390px previews had no page-wide horizontal overflow. Wide tables scrolled within their own area.
- Reference styling was limited to intended top-level paragraphs/CSL entries in the dedicated Reading-view note.
- Print-media emulation used white background, dark text, 11pt size and 1.8 line height regardless of dark mode or screen density.

Screenshots in `screenshots/` are a subset of those recorded previews. The sample research content is fictional.

## Package checks

`python3 scripts/build.py` builds directly from `src/theme.css` without depending on the previous release artifact. `python3 scripts/validate.py` checks the release metadata, required files, generated-artifact consistency, CSS size budget and runtime asset boundaries. The publication layout is separate from the manuscript project, and only explicitly selected theme files are included.

The 1.1.1 CSS keeps native underline rendering instead of setting `text-decoration-thickness`. It retains the CSS2 `text-indent` hanging-indent pattern for references and includes compatible print page-break avoidance declarations. Broad compatibility warnings for negative `text-indent` do not by themselves indicate unsupported CSS.

## Not yet directly verified

- Live native Obsidian interaction, Korean IME composition, keyboard navigation and other plugins.
- Actual PDF export and page breaks.
- Native mobile Obsidian and Obsidian 1.10.6 (the declared minimum version).
- Community directory review of 1.1.1. The 1.1.0 automated review failed; the existing Community page and a GitHub release do not prove that 1.1.1 has passed review.
