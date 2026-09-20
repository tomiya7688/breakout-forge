# v1.0.0 License and Bundled-Content Audit

This document records the repository-side license audit for Breakout Forge v1.0.0.

The final Windows ZIP is still required to pass the automated Release Gate before the audit is considered complete for a formal release.

## Breakout Forge

- License: MIT
- File: `LICENSE`
- Copyright: 2026 tomiya7688

## Runtime / packaging components

### CPython 3.12

- License: Python Software Foundation License Version 2 and historical Python licenses
- Upstream: https://www.python.org/
- Bundled license text: `third_party_licenses/Python-LICENSE.txt`

The Windows onedir artifact contains a Python runtime, so its license is included with the distribution.

### pygame

- License: GNU Lesser General Public License version 2.1
- Upstream: https://www.pygame.org/
- Main license text: `third_party_licenses/pygame-LGPL-2.1.txt`

pygame documents dependencies on SDL and multiple native libraries. Breakout Forge mirrors pygame's upstream dependency notices in:

`third_party_licenses/pygame-dependencies/`

The mirrored set currently contains 20 upstream notice files, including SDL2, SDL2_image, SDL2_mixer, FreeType, JPEG, PNG, TIFF, WebP, zlib, Ogg/Vorbis, Opus, FLAC, mpg123, PortMidi, and related components.

### Pillow

- License: MIT-CMU
- Upstream: https://python-pillow.org/
- License text: `third_party_licenses/Pillow-LICENSE.txt`

Pillow is a runtime dependency used by the Data layer to decode and preprocess stage images.

### PyInstaller

- License: GPL-2.0-or-later with the PyInstaller Bootloader Exception for bootloader/related files; selected runtime hooks/modules are Apache-2.0
- Upstream: https://pyinstaller.org/
- License text and exception: `third_party_licenses/PyInstaller-COPYING.txt`

The Bootloader Exception permits generated executable combinations to be distributed without applying the GPL to Breakout Forge solely because the PyInstaller bootloader is embedded.

## Development-only dependencies

pytest and Ruff are used for development/CI. They are not declared runtime dependencies and are not intentionally shipped as application components.

## Repository media audit

Machine-readable source of truth:

`release/asset-provenance.json`

Currently declared distributable media:

| Path | Origin | Project license |
|---|---|---|
| `stages/sample/main.png` | Generated specifically for this repository | MIT |
| `stages/layered_sample/bottom.png` | Generated specifically for this repository | MIT |
| `stages/layered_sample/top.png` | Generated specifically for this repository | MIT |

Other repository media status:

- `assets/`: no bundled media; only `.gitkeep`
- External fonts: none
- Bundled audio: none
- README/logo images: none

No third-party sample artwork is intentionally included in the official repository.

## Automated enforcement

`scripts/audit_licenses.py` verifies:

- root MIT `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- primary third-party license texts
- all 20 pygame dependency notice files
- provenance manifest schema
- every distributable media file under `assets/` and `stages/` has a provenance entry
- every provenance entry points to an actual distributable media file
- pygame / Pillow / PyInstaller are present in the release-validation environment

Adding a new PNG, JPEG, WebP, SVG, audio file, or font without updating the provenance manifest makes the audit fail.

The Release Gate runs this audit on both Linux source validation and Windows release validation.

## Distribution requirements

`scripts/prepare_dist.py` includes the following beside the executable:

- `LICENSE`
- `THIRD_PARTY_NOTICES.md`
- `third_party_licenses/`

Regular Build Check and formal release acceptance both require these paths to exist.

## User MODs and user content

User-added stages, images, and Python MODs are outside the official repository's bundled-content audit.

Breakout Forge does not guarantee the copyright status, license compatibility, or safety of user-provided content. Python MODs are unsandboxed and should only be installed from trusted sources.

## Final release-only verification still required

Before v1.0.0 is formally published:

- Release Gate must build the actual Windows onedir artifact.
- The release acceptance check must confirm the notice bundle is in the built artifact.
- The ZIP must be extracted into a clean directory and pass the same acceptance check.
- Any unexpected native binary introduced by dependency/version changes must be reviewed before release.
- #30 integrated acceptance must pass.
- There must be no release-blocker or must-fix known bugs.

The actual GitHub Actions run and generated ZIP are the final source of truth for the binary-distribution portion of this audit.
