#!/usr/bin/env bash
# Fetch MoreWaita, build MoreWaita-Folders, install both to ~/.local/share/icons
# and (unless --no-activate) make MoreWaita-Folders the GNOME icon theme.
#
#   ./install.sh [--no-activate] [--ref <MoreWaita git ref>]
set -euo pipefail
cd "$(dirname "$0")"

ACTIVATE=1
REF=""
while [ $# -gt 0 ]; do
    case "$1" in
        --no-activate) ACTIVATE=0 ;;
        --ref) REF="$2"; shift ;;
        -h|--help) sed -n '2,6p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 1 ;;
    esac
    shift
done

for cmd in git python3 magick gtk-update-icon-cache; do
    command -v "$cmd" >/dev/null || { echo "missing: $cmd" >&2; exit 1; }
done

ICONS="${XDG_DATA_HOME:-$HOME/.local/share}/icons"
MW=.cache/MoreWaita

if [ -d "$MW/.git" ]; then
    git -C "$MW" fetch --quiet --depth 1 origin "${REF:-HEAD}"
    git -C "$MW" checkout --quiet FETCH_HEAD
else
    mkdir -p .cache
    git clone --quiet --depth 1 https://github.com/somepaulo/MoreWaita.git "$MW"
    [ -n "$REF" ] && { git -C "$MW" fetch --quiet --depth 1 origin "$REF"; git -C "$MW" checkout --quiet FETCH_HEAD; }
fi
echo "MoreWaita $(git -C "$MW" rev-parse --short HEAD)"

rm -rf build
python3 -I build.py --morewaita "$MW" --out build/MoreWaita-Folders

# MoreWaita's own installer copies to ~/.local/share/icons/MoreWaita (non-root)
THEMEDIR="$ICONS/MoreWaita/" bash "$MW/install.sh" >/dev/null

rm -rf "$ICONS/MoreWaita-Folders"
cp -r build/MoreWaita-Folders "$ICONS/"
gtk-update-icon-cache -q -f -t "$ICONS/MoreWaita-Folders"
echo "installed to $ICONS/MoreWaita and $ICONS/MoreWaita-Folders"

if [ "$ACTIVATE" = 1 ]; then
    gsettings set org.gnome.desktop.interface icon-theme MoreWaita-Folders
    echo "icon theme set to MoreWaita-Folders (undo: gsettings set org.gnome.desktop.interface icon-theme Adwaita)"
fi
echo "next: ./apply-folder-icons.sh --dry-run   (uses folders.local.conf, else the example folders.conf)"
