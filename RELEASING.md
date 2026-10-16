# Releasing Seojae

Repository: `takjakim/obsidian-seojae`. The publication repository contains only the theme, its sample notes, screenshots and release tooling.

## Prepare a version

1. Update `manifest.json` with an `x.y.z` version and the actual minimum supported Obsidian version. Keep the theme name `Seojae`.
2. Add the same version/minimum-version pair to `versions.json`.
3. Update the source CSS version comment, release notes and screenshots as needed.
4. Run `python3 scripts/build.py` and `python3 scripts/validate.py`.
   The build is derived from `src/theme.css` and does not require a previous release artifact. The validator's 100,000-byte CSS budget is a conservative project safeguard, not an official Obsidian limit; it also rejects embedded or runtime font assets.
5. Test the theme in a separate Obsidian vault, including Live Preview, Korean input, light/dark mode, Style Settings and PDF export. Record any unverified behavior honestly.
6. Commit the exact release files on `main`.

CI repeats validation and regression tests for the build and release safeguards. Keep local and CI checks green before publishing.

## Publish with GitHub CLI

```sh
bash scripts/publish.sh
```

The publishing script checks the current repository and GitHub identity, creates the public repository if needed, pushes `main` and a version tag, then publishes the release with `theme.css` and `manifest.json` as separate assets. It does not force-push, overwrite existing assets, or register the theme in the Obsidian directory.

The release tag must exactly match the manifest version, for example `1.1.1`, not `v1.1.1`. Run the script only when that version is ready for public release.

## Submit to Obsidian Community

Current submission process, checked on 2026-10-15:

The Community page is <https://community.obsidian.md/themes/seojae>. The 1.1.0 automated review failed; a published GitHub release or an existing page must not be described as accepted until the corrected version passes review.

1. Sign in at <https://community.obsidian.md> with the owner's Obsidian account.
2. Link the owner's GitHub account.
3. Select **Themes → New theme**.
4. Use the public repository URL `https://github.com/takjakim/obsidian-seojae`.
5. Use a current theme screenshot path, initially `screenshots/light.png`, and select both **Light** and **Dark**. The existing image is a browser-rendered preview; replace it with a native Obsidian screenshot if the review requires one. The recommended thumbnail size is 512 × 288.
6. Review the developer policies and maintenance commitment, then submit.
7. Resolve automated review errors with an incremented release, ask the directory to check for the new release, and publish the entry only after review succeeds.

The directory reads the default branch's `manifest.json` and downloads the two assets from the matching published release. A GitHub release alone does not mean the theme has been accepted into the directory.

After the first accepted submission, release new versions through GitHub. If discovery is delayed, the directory management page offers **Check for new releases**. End users still choose to update in Obsidian; the theme contains no self-update code.

References:

- [Official submission guide](https://docs.obsidian.md/themes/app-themes/submit-theme)
- [Account linking and ownership](https://docs.obsidian.md/community-directory/set-up-and-claim)
- [Developer policies](https://docs.obsidian.md/community-directory/developer-policies)
- [Directory FAQ](https://docs.obsidian.md/community-directory/faq)
- [Official theme template](https://github.com/obsidianmd/obsidian-sample-theme)
