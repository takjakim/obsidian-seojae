# Seojae 1.1.1

This release fixes the package-size rejection reported for 1.1.0.

- Removed all embedded font data, reducing `theme.css` from 8,199,325 bytes to 16,679 bytes.
- Uses installed Times New Roman for Latin text and installed Nanum Myeongjo for Korean text, with Noto Serif CJK KR and serif fallbacks.
- Added build, validation and CI safeguards against bundled or runtime font assets and oversized CSS.
- Preserved native link underlines, CSS2-compatible reference hanging indents and print page-break avoidance.

1.1.0의 용량 문제를 해결한 릴리스입니다. 글꼴은 더 이상 테마에 포함되거나 자동으로 다운로드되지 않습니다. 모든 기기에 [나눔명조 Regular와 Bold](https://fonts.google.com/specimen/Nanum+Myeongjo)를 설치한 뒤 Obsidian을 다시 시작하세요. 설치된 글꼴은 오프라인에서도 사용할 수 있으며, 글꼴이 없으면 대체 serif 글꼴이 적용됩니다.

Try the [Seojae Community page](https://community.obsidian.md/themes/seojae) first. If 1.1.1 is not yet available there, download **both `theme.css` and `manifest.json`** into `<vault>/.obsidian/themes/Seojae/`, then select Seojae in Settings → Appearance.

The minimum version declared by the manifest is Obsidian 1.10.6. The 1.1.1 browser preview used Obsidian 1.14.4 CSS; native editor/IME behavior, PDF pagination, mobile and the minimum supported version have not yet been directly tested. Screenshots show a rendered sample rather than a live vault.

Theme: [MIT](LICENSE). No fonts are included in this release. The historical 1.1.0 font license remains available at the [1.1.0 tag](https://github.com/takjakim/obsidian-seojae/blob/1.1.0/FONT-LICENSE.txt).
