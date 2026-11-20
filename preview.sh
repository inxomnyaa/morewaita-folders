#!/usr/bin/env bash
# Render this theme's own icons (the ICONS table in build.py) into one labelled PNG.
# The copied MoreWaita folder/file icons are left out.
#   ./preview.sh [OUT.png]      (default: build/preview.png)
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-build/preview.png}"
args=()
while read -r n; do
    args+=(-label "${n#folder-}" "build/MoreWaita-Folders/scalable/places/$n.svg")
done < <(python3 -I -c 'import importlib.util as u; s=u.spec_from_file_location("b","build.py"); b=u.module_from_spec(s); s.loader.exec_module(b); print("\n".join(sorted(b.ICONS)))')
magick montage -density 96 -background white -pointsize 11 "${args[@]}" \
    -tile 8x -geometry 110x110+8+4 "$OUT"
echo "$OUT"
