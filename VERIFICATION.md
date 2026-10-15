# Verification record — 1.1.0

The theme package derives from the Seojae 1.1.0 build verified on 2026-10-15. These checks used a browser fixture with the locally installed Obsidian 1.13.7 base CSS; that proprietary base CSS is not included in this repository.

## Recorded preview checks

- CSS parsing reported no top-level syntax errors. Style Settings declarations parsed successfully.
- Actual rendered glyphs were NanumMyeongjo, NanumMyeongjoBold, TimesNewRomanPSMT and TimesNewRomanPS-BoldMT; code used Menlo.
- Embedded font data matched the original font SHA-256 values, including when local-font sources were disabled in the fixture.
- Text contrast combinations exceeded 4.5:1 in the tested light/dark surfaces.
- Reading density, custom line/paragraph spacing, footnote scale, readable width and user text-size precedence behaved as documented.
- 320px and 390px previews had no page-wide horizontal overflow. Wide tables scrolled within their own area.
- Reference styling was limited to intended top-level paragraphs/CSL entries in the dedicated Reading-view note.
- Print-media emulation used white background, dark text, 11pt size and 1.8 line height regardless of dark mode or screen density.

Screenshots in `screenshots/` are a subset of those recorded previews. The sample research content is fictional.

## Publication checks

`python3 scripts/validate.py` checks the release metadata, embedded font identity, required files and runtime asset boundaries. The publication layout is separate from the manuscript project, and only explicitly selected theme files are included.

## Not yet directly verified

- Live native Obsidian interaction, Korean IME composition, keyboard navigation and other plugins.
- Actual PDF export and page breaks.
- Native mobile Obsidian and Obsidian 1.10.6 (the declared minimum version).
- Community directory review and installation; these are only complete when the published entry is accepted and installable.
