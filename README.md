# MoreWaita-Folders

Folder icons for GNOME Files, built on top of [MoreWaita](https://github.com/somepaulo/MoreWaita) (not a fork).

![preview](docs/preview.png)

## Install

Needs `git`, `python3`, ImageMagick 7 and `gtk-update-icon-cache`.

```sh
./install.sh
```

This downloads MoreWaita, builds the theme, installs both to `~/.local/share/icons/`, and sets `MoreWaita-Folders` as your icon theme. To skip setting the theme, pass `--no-activate`.

## Apply icons to folders

Standard folders like Music and Downloads get their icons automatically. For other folders, copy `folders.conf` to `folders.local.conf` and list each folder with an icon name, then a path relative to your home folder:

```
folder-games            Games
folder-emu-switch       ROMs/Switch
```

```sh
./apply-folder-icons.sh --dry-run
./apply-folder-icons.sh
nautilus -q    # restart Files to see the change
```

The icon names are the file names in the preview, with `folder-` in front, for example `folder-emu-gba` or `folder-keg`.

## Make new icons

Add a line to `ICONS` in `build.py`:

```python
"folder-foo": "adw:some-glyph",   # Adwaita's some-glyph-symbolic.svg
"folder-foo": "own:foo",          # glyphs/foo.svg, 16x16, drawn with currentColor
"folder-foo": "mw:folder-bar",    # emblem from MoreWaita's folder-bar
```

Run `python3 build.py && ./preview.sh` and check `build/preview.png`, then run `./install.sh`. Emblems are scaled to the same size automatically.

## Remove

```sh
./apply-folder-icons.sh --reset
/usr/bin/gsettings set org.gnome.desktop.interface icon-theme Adwaita
rm -rf ~/.local/share/icons/MoreWaita-Folders ~/.local/share/icons/MoreWaita
```

## License

GPL-3.0, like MoreWaita. Uses MoreWaita's folder shape and emblems, plus Adwaita symbolic glyphs (CC-BY-SA 3.0 / LGPL-3.0). The PlayStation logo is from Simple Icons (CC0), the N64 logo from file-icons (ISC, © John Gardner); both are trademarks of their owners.
