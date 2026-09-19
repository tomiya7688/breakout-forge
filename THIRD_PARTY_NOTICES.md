# Third-Party Notices

Breakout Forge itself is licensed under the MIT License. See `LICENSE`.

The Windows `--onedir` distribution also contains third-party runtime software.
The corresponding license texts are shipped in `third_party_licenses/`.

## Python

- Component: CPython 3.12 runtime and standard library
- License: Python Software Foundation License Version 2 and historical Python licenses
- Project: https://www.python.org/
- License text: `third_party_licenses/Python-LICENSE.txt`

## pygame

- Component: pygame
- License: GNU Lesser General Public License version 2.1
- Project: https://www.pygame.org/
- License text: `third_party_licenses/pygame-LGPL-2.1.txt`
- pygame links to and/or bundles SDL and other native libraries. Their upstream license notices are mirrored under `third_party_licenses/pygame-dependencies/`.

Breakout Forge does not modify pygame. The packaged distribution keeps pygame/native shared libraries as separate files under the onedir `_internal/` tree rather than statically incorporating them into Breakout Forge source.

## Pillow

- Component: Pillow
- License: MIT-CMU
- Project: https://python-pillow.org/
- License text: `third_party_licenses/Pillow-LICENSE.txt`

Pillow may itself use native image-codec libraries supplied by the installed wheel. The Release Gate inventories the built distribution so additions to the native runtime remain visible during release review.

## PyInstaller

- Component: PyInstaller bootloader and run-time support used by the packaged executable
- License: GPL-2.0-or-later with the PyInstaller Bootloader Exception for the bootloader; some run-time hooks/modules are Apache-2.0
- Project: https://pyinstaller.org/
- License text and exception: `third_party_licenses/PyInstaller-COPYING.txt`

The PyInstaller bootloader exception explicitly permits distributing generated executable combinations without imposing GPL terms on the application solely because the bootloader is embedded.

## Development-only tools

pytest and Ruff are development/CI tools and are not intentionally included as Breakout Forge runtime dependencies.

## User content and MODs

Files, images, stages, and Python MODs added by users are not supplied by the Breakout Forge project. Their copyright, licensing, and safety remain the responsibility of their respective authors/distributors.
