# CLAUDE.md

Notes for Claude (or any coding agent) working on this repo. The human docs are in README.md.

## What this is
An add-on GNOME icon theme, `MoreWaita-Folders` (inherits MoreWaita → Adwaita → hicolor). It's generated, not hand-drawn. `build.py` combines MoreWaita's folder shape with an emblem from Adwaita, from `glyphs/`, or from another MoreWaita icon. It then renders each emblem with ImageMagick, measures it, and scales it to the size of `REF` (`user-desktop`), so all folders look the same size.

## Files
- `build.py`: generator. The `ICONS` dict is the only thing you usually edit.
- `glyphs/*.svg`: own emblems on a 16×16 grid, drawn with `currentColor`, 2px strokes (Adwaita's weight), round joins and caps. Keep the outline inside 1..15, or the stroke gets clipped. `logo-*.svg` keep their original viewBox; `build.py` reads it.
- `install.sh`: clones or updates MoreWaita into `.cache/`, builds, installs to `~/.local/share/icons/`, and sets gsettings. `--no-activate` skips gsettings.
- `apply-folder-icons.sh` + `folders.local.conf` (the user's real list, gitignored) or `folders.conf` (a generic example): set `metadata::custom-icon-name` on folders via `gio`. Config lines are `<icon> <path>`, with the path relative to `$HOME`. Never put the user's personal folder names into the committed `folders.conf`.
- `preview.sh`: writes `build/preview.png`, a contact sheet of all built icons. Look at it after every glyph change.
- `.cache/`, `build/`: gitignored.

## Workflow for changes
1. Edit `ICONS` and/or `glyphs/`.
2. Run `python3 -I build.py && ./preview.sh`, then view `build/preview.png`. Check size and centring against `user-desktop`.
3. Show the user the preview and wait for an OK before installing or applying (`./install.sh`, `./apply-folder-icons.sh`). Run `apply-folder-icons.sh --dry-run` first.
4. Refresh `docs/preview.png` with `./preview.sh docs/preview.png` if the README picture should change.

## Gotchas
- **Hidden drawings in Adwaita glyphs.** Some Adwaita symbolic SVGs, such as `application-x-executable`, contain leftover drawings outside the 16×16 viewBox. Glyphs are wrapped in a nested `<svg overflow="hidden">` to clip them. Don't remove that wrapper.
- **Colours.** Adwaita glyphs hard-code `fill="#2e3436"`. `glyph_markup` strips hex fills and sets the MoreWaita blue `#438de6`. Own glyphs use `currentColor`, which gets replaced with that blue.
- **The MoreWaita base is split by element ids** (`BASE_IDS`: `g760`, `rect1135`, `path1953`, `rect1586`). Every other top-level element apart from `defs` and `linearGradient` is treated as emblem. If MoreWaita redraws its folders, those ids may change and `build.py` will produce folders with no shape, or emblems that include the folder. Check the preview after updating MoreWaita, and pin a version with `install.sh --ref` if needed.
- **Some MoreWaita icons don't fit that structure.** `folder-projects`, for example, has bare paths instead of the `g760` group, so its folder paths have other ids. They still work because only the emblem is lifted, while the folder shape always comes from `BASE_ICON` (`folder-games`).
- **Measuring uses `magick` at 384 dpi** (4× the 96 dpi default). The result is divided by 4. If ImageMagick has no librsvg delegate, its internal renderer may mis-measure nested SVGs. Check `magick -list format | grep SVG`.
- **Same name, theme wins.** Icon names in this theme override MoreWaita's (for example `folder-appimage`). That's intentional, but new names should use a prefix like `folder-emu-*` unless an override is meant.
- **Use the system `gsettings`.** Homebrew's `gsettings` writes to a memory backend and reports success, but GNOME never sees the change. Check with `dconf read /org/gnome/desktop/interface/icon-theme`. `install.sh` prefers `/usr/bin/gsettings`.
- **Use the system `gio`.** A Homebrew `gio` earlier in PATH lacks the GVFS module and fails with "Setting attribute metadata::custom-icon-name not supported". `apply-folder-icons.sh` prefers `/usr/bin/gio`, and you can override it with `GIO=...`. Use `/usr/bin/gio info -a metadata::custom-icon-name <dir>` to check a folder by hand.
- **Nautilus caches icons.** Run `nautilus -q` after reinstalling. `gtk-update-icon-cache` is run by `install.sh`.

## Don'ts
- Don't commit MoreWaita or Adwaita files, or generated icons, apart from `docs/preview.png`. They're fetched or read at build time.
- Logos (`glyphs/logo-*.svg`) only from permissively licensed sets (Simple Icons CC0, file-icons ISC, ...). Keep the source/licence/trademark comment at the top of the file. Everything else in `glyphs/` is drawn in-house.
- Don't install system-wide, and don't touch `/usr`. Everything goes in `~/.local/share/icons`.
