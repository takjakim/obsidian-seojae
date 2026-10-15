# 서재 · Seojae

A quiet Obsidian theme for Korean academic writing, with warm light colors, a muted dark palette, and bilingual serif typography.

국문 논문을 오래 읽고 쓰기 위한 Obsidian 테마입니다. 한글은 **나눔명조**, 영문은 **Times New Roman**을 사용합니다.

![Seojae light theme — rendered sample manuscript](screenshots/light.png)

## Features

- Light and dark modes with restrained colors and underlined links.
- Original Nanum Myeongjo Regular and Bold embedded in the theme for offline use.
- Times New Roman for Latin text when installed on the device; system fonts for the interface and monospace fonts for code.
- Adjustable reading width, density, paragraph spacing and footnote size through the optional **Style Settings** plugin.
- Reference-note hanging indents in Reading view with `cssclasses: seojae-references`.
- A4-oriented print styling, with an 11pt body and 1.8 line spacing.

No plugin is required. Defaults are a 684px readable width, 1.9 line spacing, 0.95rem paragraph spacing and footnotes at 86% of body size. Obsidian's text-size setting remains available.

![Seojae dark theme — rendered sample manuscript](screenshots/dark.png)

These images show a browser preview rendered with the installed Obsidian 1.13.7 base CSS and a fictional sample manuscript. They are not screenshots of a live vault. Native Obsidian interaction, Korean IME input and PDF pagination still need testing.

## Install

Until the theme is listed in the Community directory:

1. Download `theme.css` and `manifest.json` from a [published release](https://github.com/takjakim/obsidian-seojae/releases).
2. Put both files directly inside `<vault>/.obsidian/themes/Seojae/`.
3. Open **Settings → Appearance → Themes** and select **Seojae**. Restart Obsidian if it is not listed.

Turn on **Settings → Editor → Readable line length** to use the theme's reading width. Install the optional **Style Settings** community plugin to adjust the theme controls; the current control labels are Korean.

See the [한국어 사용 안내](GUIDE.ko.md) and [sample notes](examples/) for details. The theme does not check citations or guarantee compliance with a university's thesis formatting rules.

## Fonts and licenses

The theme CSS is licensed under the [MIT License](LICENSE). The original Nanum Myeongjo font files are embedded without modification under the [SIL Open Font License 1.1](FONT-LICENSE.txt). Font copyright and license notices are also embedded in `theme.css` so they accompany the two-file Obsidian installation.

Times New Roman is **not bundled**. It is used only when available on the user's device; otherwise a serif fallback is used. The theme makes no network requests for fonts, images or updates.

## Development

Edit `src/theme.css`, then build and validate with Python 3:

```sh
python3 scripts/build.py
python3 scripts/validate.py
```

The builder reuses the verified original font data embedded in the checked-in `theme.css`. No package installation or font download is required. See [RELEASING.md](RELEASING.md) for versioning, GitHub releases and Community directory submission.

## Verification scope

The 1.1.0 preview checks covered light/dark text contrast, embedded font identity, reading-density presets, narrow layouts, reference styling and print CSS. The manifest declares Obsidian 1.10.6 or later; direct execution on that minimum version and on mobile remains unverified. See [VERIFICATION.md](VERIFICATION.md) for the recorded scope and limitations.

Report reproducible problems with your Obsidian version, operating system, light/dark mode and relevant Style Settings values. Use a minimal sample note without private research material.
