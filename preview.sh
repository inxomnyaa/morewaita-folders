#!/usr/bin/env bash
# Render every built icon into one labelled PNG (default: build/preview.png).
#   ./preview.sh [OUT.png]
set -euo pipefail
cd "$(dirname "$0")"
OUT="${1:-build/preview.png}"
args=()
for f in build/MoreWaita-Folders/scalable/places/*.svg; do
    n=$(basename "$f" .svg)
    args+=(-label "${n#folder-}" "$f")
done
magick montage -density 96 -background white -pointsize 11 "${args[@]}" \
    -tile 8x -geometry 110x110+8+4 "$OUT"
echo "$OUT"
