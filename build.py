#!/usr/bin/env python3
"""Build the MoreWaita-Folders icon theme.

    ./build.py [--morewaita DIR] [--out DIR]

Makes MoreWaita-style folder icons whose emblems come from
  adw:<name>  Adwaita symbolic glyph  (/usr/share/icons/Adwaita/symbolic/*/<name>-symbolic.svg)
  own:<name>  a 16x16 glyph in ./glyphs/<name>.svg, drawn with currentColor
  mw:<name>   the emblem of an existing MoreWaita folder icon (re-scaled)

Every emblem is rendered with ImageMagick, measured, then scaled so its longest
side matches the REF icon's and centred on the folder front. That keeps all
folders the same visual size, whatever the glyph source.
"""
import argparse, pathlib, re, subprocess, sys, tempfile
import xml.etree.ElementTree as ET

HERE = pathlib.Path(__file__).resolve().parent
ADW = pathlib.Path("/usr/share/icons/Adwaita/symbolic")
COLOR = "#438de6"                      # MoreWaita emblem blue
REF = "user-desktop"                   # every emblem is scaled to this one's size
CX, CY = 63.98, 77.41                  # emblem centre on the 128px folder
GLYPH_BOX = (40.715766, 54.144588, 46.534498)  # x, y, size of a 16px glyph on the folder (MoreWaita's own placement)
BASE_ICON = "folder-games"             # MoreWaita icon whose folder shape is reused
BASE_IDS = {"g760", "rect1135", "path1953", "rect1586"}  # ids of MoreWaita's folder shape
SVGNS, XLINK = "http://www.w3.org/2000/svg", "http://www.w3.org/1999/xlink"

# icon name -> emblem source. Add lines here to get new icons.
ICONS = {
    # XDG user folders: GIO asks for these names; Adwaita only ships them at 16px.
    "folder-music": "adw:folder-music",
    "folder-videos": "adw:folder-videos",
    "folder-pictures": "adw:folder-pictures",
    "folder-documents": "adw:folder-documents",
    "folder-download": "adw:folder-download",
    "user-desktop": "adw:video-display",          # Adwaita's own desktop glyph is a folder-in-folder
    "folder-templates": "adw:folder-templates",
    "folder-publicshare": "adw:folder-publicshare",
    # override MoreWaita's arrow+gear
    "folder-appimage": "adw:application-x-executable",
    # consoles (original line drawings in glyphs/, no logos)
    "folder-emu-gameboy": "own:gameboy",
    "folder-emu-gba": "own:gba",
    "folder-emu-gbasp": "own:gbasp",
    "folder-emu-nds": "own:nds",
    "folder-emu-3ds": "own:3ds",
    "folder-emu-switch": "own:switch",
    "folder-emu-wiiu": "own:wiiu",
    "folder-emu-amiibo": "own:amiibo",
    "folder-emu-nes": "own:nes",
    "folder-emu-snes": "own:snes",
    "folder-emu-n64": "own:logo-n64",
    "folder-emu-gamecube": "own:gamecube",
    "folder-emu-wii": "own:wii",
    "folder-emu-playstation": "own:logo-playstation",
    "folder-emu-psp": "own:psp",
    "folder-emu-arcade": "own:arcade",
    "folder-code": "own:code",                    # MoreWaita's brackets are thinner than everything else
    "folder-keg": "own:keg",                      # Homebrew / Decky "homebrew" folder
    # MoreWaita icons re-scaled to match (MoreWaita draws emblems in a 32px box, Adwaita glyphs fill ~47px)
    **{n: f"mw:{n}" for n in [
        "folder-projects", "folder-games", "folder-backup", "folder-3dbenchy",
        "folder-games-card", "folder-roms", "folder-computer", "folder-windows",
    ]},
}

ET.register_namespace("", SVGNS)
ET.register_namespace("xlink", XLINK)


def tag(e):
    return e.tag.split("}")[-1]


def split_morewaita(path):
    """Return (root, emblem elements) of a MoreWaita folder icon; root keeps only the folder shape."""
    root = ET.parse(path).getroot()
    emblem = [e for e in root if tag(e) not in ("defs", "linearGradient") and e.get("id") not in BASE_IDS]
    for e in emblem:
        root.remove(e)
    return root, emblem


def glyph_markup(spec):
    kind, name = spec.split(":", 1)
    if kind == "adw":
        hits = list(ADW.glob(f"*/{name}-symbolic.svg"))
        if not hits:
            sys.exit(f"no Adwaita glyph {name}-symbolic.svg under {ADW}")
        f = hits[0]
    else:
        f = HERE / "glyphs" / f"{name}.svg"
    m = re.search(r"<svg([^>]*)>(.*)</svg>", f.read_text(), re.S)
    vb = re.search(r'viewBox="([^"]+)"', m.group(1))
    viewbox = vb.group(1) if vb else "0 0 16 16"  # logos come in other sizes; measuring rescales them
    inner = m.group(2)
    inner = re.sub(r'\sfill="#[0-9a-fA-F]+"', "", inner)  # drop Adwaita's hardcoded #2e3436
    inner = inner.replace("currentColor", COLOR)
    x, y, s = GLYPH_BOX
    # nested <svg> clips to the glyph's box: some Adwaita glyphs hide extra drawings outside it
    return (f'<svg xmlns="{SVGNS}" x="{x}" y="{y}" width="{s}" height="{s}" viewBox="{viewbox}" '
            f'overflow="hidden"><g fill="{COLOR}">{inner}</g></svg>')


def emblem(spec, mw):
    """(defs elements, emblem markup) in 128px icon coordinates, before scaling."""
    if spec.startswith("mw:"):
        root, parts = split_morewaita(mw / "scalable/places" / f"{spec[3:]}.svg")
        defs = [c for d in root if tag(d) == "defs" for c in d]
        return defs, "".join(ET.tostring(p, encoding="unicode") for p in parts)
    return [], glyph_markup(spec)


def measure(defs, body):
    """Bounding box (x, y, w, h) of the drawn emblem, in 128px units."""
    d = "".join(ET.tostring(c, encoding="unicode") for c in defs)
    svg = (f'<svg xmlns="{SVGNS}" xmlns:xlink="{XLINK}" width="128" height="128" '
           f'viewBox="0 0 128 128"><defs>{d}</defs>{body}</svg>')
    with tempfile.NamedTemporaryFile("w", suffix=".svg") as t:
        t.write(svg)
        t.flush()
        out = subprocess.run(["magick", "-density", "384", "-background", "none", t.name,
                              "-trim", "-format", "%w %h %X %Y", "info:"],
                             capture_output=True, text=True, check=True).stdout.split()
    w, h, x, y = (float(v) / 4 for v in out)  # 384 dpi = 4x the 96 dpi default
    return x, y, w, h


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--morewaita", type=pathlib.Path, default=HERE / ".cache/MoreWaita",
                    help="MoreWaita source checkout (default: .cache/MoreWaita)")
    ap.add_argument("--out", type=pathlib.Path, default=HERE / "build/MoreWaita-Folders")
    a = ap.parse_args()

    base_root, _ = split_morewaita(a.morewaita / "scalable/places" / f"{BASE_ICON}.svg")
    base_ids = {e.get("id") for e in base_root.iter() if e.get("id")}
    base = ET.tostring(base_root, encoding="unicode")
    base = base[: base.rindex("</svg>")]

    icons = {n: emblem(s, a.morewaita) for n, s in ICONS.items()}
    boxes = {n: measure(*e) for n, e in icons.items()}
    for n, (defs, body) in icons.items():  # warn about glyphs drawn past their grid (they get cut off)
        if 'overflow="hidden"' in body and ICONS[n].startswith("own:"):
            free = measure(defs, body.replace('overflow="hidden"', 'overflow="visible"'))
            if any(abs(a - b) > 0.3 for a, b in zip(free, boxes[n])):
                print(f"  WARNING {n}: {ICONS[n]} reaches past the 16px grid and is clipped", file=sys.stderr)
    target = max(boxes[REF][2:])

    places = a.out / "scalable/places"
    places.mkdir(parents=True, exist_ok=True)
    for name, (defs, body) in icons.items():
        x, y, w, h = boxes[name]
        k = target / max(w, h)
        tx, ty = CX - k * (x + w / 2), CY - k * (y + h / 2)
        extra = "".join(ET.tostring(c, encoding="unicode") for c in defs if c.get("id") not in base_ids)
        svg = (base + (f"<defs>{extra}</defs>" if extra else "")
               + f'<g transform="matrix({k:.5f},0,0,{k:.5f},{tx:.4f},{ty:.4f})">{body}</g></svg>\n')
        (places / f"{name}.svg").write_text(svg)
        print(f"  {name:22} {ICONS[name]:34} {w:5.1f}x{h:5.1f}  x{k:.2f}")

    (a.out / "index.theme").write_text("""[Icon Theme]
Name=MoreWaita-Folders
Comment=MoreWaita with large XDG folder icons, console folders and size-matched emblems
Inherits=MoreWaita,Adwaita,hicolor
Directories=scalable/places

[scalable/places]
Size=128
MinSize=8
MaxSize=512
Type=Scalable
Context=Places
""")
    print(f"built {len(ICONS)} icons -> {a.out}")


if __name__ == "__main__":
    main()
