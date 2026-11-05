#!/usr/bin/env bash
# Give folders custom icons (GIO metadata, the same thing Files' Properties dialog sets).
#
#   ./apply-folder-icons.sh [--dry-run] [--reset] [CONFIG]   (default: folders.local.conf if present, else folders.conf)
#
# CONFIG lines: <icon-name> <path>   path is the rest of the line (spaces OK),
#               relative to $HOME unless absolute. Lines starting with # are comments.
# --reset removes the custom icon from every folder listed instead.
# Missing folders are skipped. XDG folders (Music, Videos, ...) need no entry.
set -euo pipefail

DRY=0 RESET=0 CONF=""
for a in "$@"; do
    case "$a" in
        --dry-run) DRY=1 ;;
        --reset) RESET=1 ;;
        -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
        *) CONF="$a" ;;
    esac
done
D="$(dirname "$0")"
if [ -z "$CONF" ]; then [ -f "$D/folders.local.conf" ] && CONF="$D/folders.local.conf" || CONF="$D/folders.conf"; fi
echo "using $CONF"

# Prefer the system gio: other builds (e.g. Homebrew's) lack the GVFS module and
# fail with "Setting attribute metadata::custom-icon-name not supported".
GIO="${GIO:-$( [ -x /usr/bin/gio ] && echo /usr/bin/gio || command -v gio )}"

run() { if [ "$DRY" = 1 ]; then echo "    would run: $*"; else "$@"; fi; }

while read -r icon path; do
    [[ -z "$icon" || "$icon" == \#* ]] && continue
    [[ "$path" == /* ]] || path="$HOME/$path"
    if [ ! -d "$path" ]; then echo "skip (missing)          $path"; continue; fi
    if [ "$RESET" = 1 ]; then
        echo "reset                   $path"
        run "$GIO" set -d "$path" metadata::custom-icon-name
    else
        printf '%-23s %s\n' "$icon" "$path"
        run "$GIO" set "$path" metadata::custom-icon-name "$icon"
    fi
done < "$CONF"

if [ "$DRY" = 1 ]; then echo "(dry run, nothing changed)"; else echo "done. If Files doesn't update: nautilus -q"; fi
