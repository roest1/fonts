# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = ["nanoemoji==0.16.0", "fonttools==4.68.0"]
# ///
"""Build a color icon font from Material Icon Theme.

    uv run mkicons.py

Fetches the upstream release pinned in UPSTREAM below and writes, next to this
file, the font, the table that says which code point is which icon, and
upstream's license. Run by hand after an upstream release (README.md), never
at install time: what it writes is committed, so a machine that uses the icons
needs no python, no network and no font tooling.

The output is a pure function of the upstream release and the packages pinned
in mkicons.py.lock, byte for byte, and CI regenerates it to prove the committed
files are what this script writes.

WHY THIS EXISTS
---------------
A terminal draws a file's icon as a character, so an icon set has to be a font.
Nerd Fonts are that for single-color glyphs. Material Icon Theme is 1256 icons
in color, published as SVG for editors that can draw SVG; a terminal cannot.
A COLR font is the same pictures as layered glyphs, each layer a flat color,
which FreeType and so wezterm draw in color at any size.

COLR version 0, the flat one. Version 1 adds gradients, which fourteen of the
icons use and which this loses: each gradient becomes one of its colors. The
trade is that version 0 is drawn by everything that draws color fonts at all.

WHERE THE ICONS LIVE
--------------------
Supplementary Private Use Area-B, U+100000 and up, one code point an icon in
the order of their names. Nothing else is assigned there: Nerd Fonts stay in
the BMP private use area and Plane 15, so the two sets can be on screen at
once and a font can be asked for one without answering for the other.

A code point is only stable for one upstream release. A new icon is inserted
where its name sorts, and everything after it moves. That is affordable because
nothing is meant to know a code point: material-icons.tsv is written in the
same run and committed in the same change, and whoever draws an icon reads it
from there.

THE TABLE
---------
material-icons.tsv, three tab-separated columns, sorted, `#` for comments:

    icon         rust          100439     an icon and its code point, in hex
    ext          rs            rust       a file extension and its icon
    file         readme.md     readme     a whole file name
    folder       src           folder-src
    lang         git-commit    git        an editor's language id
    default      file          file       what a thing with no icon of its own gets

An open folder's icon is its closed one's name with `-open` on the end, always:
`folder-src-open`. Upstream lists every one of those out; the build checks the
rule holds and leaves them out, which is a third of the file.

The associations are upstream's own, out of the manifest its editor extension
ships, for a dark background. They are here so that nobody has to restate which
icon a README gets.

THE EZA THEME
-------------
eza/theme.yml is the same table for the one reader that cannot take it as a
table. eza draws a file's icon from a list compiled into it, and since 0.20 a
theme.yml can replace the icon for a name or an extension. Point eza at it:

    EZA_CONFIG_DIR=<this directory>/eza  EZA_ICON_SPACING=2  eza --icons

It is less than the table, because eza matches less than an editor does:

  - A name is matched exactly, case and all, where the editor ignores case. So
    a name is written as upstream has it and again the two ways people really
    spell it: `readme.md`, `Readme.md`, `README.md`.
  - An extension is what follows the LAST dot. `d.ts` cannot be said, and a
    `.d.ts` file gets the `ts` icon.
  - A name is a name: a folder called `docs` and a file called `docs` get one
    icon. Where upstream gives both, the file's wins.
  - THERE IS NO SAYING WHAT EVERYTHING ELSE GETS. A folder or a file with no
    icon of its own keeps eza's built-in glyph, so a listing is this set for
    what it knows and a Nerd Font glyph for what it does not.
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

# The npm release, and not the repository at a tag: a registry tarball never
# changes once published, and it carries the generated manifest and the 348
# recolored clones the manifest names, neither of which is in the repository.
VERSION = "5.40.0"
UPSTREAM = f"https://registry.npmjs.org/material-icon-theme/-/material-icon-theme-{VERSION}.tgz"
UPSTREAM_SHA256 = "6ea13a2dece7ca953c0315b1e93348660c02bb235706275d215be69f09d98efb"

FAMILY = "Material Icon Theme"
FONT = "MaterialIconTheme.ttf"
TABLE = "material-icons.tsv"
EZA = "eza/theme.yml"
LICENSE = "MIT-material-icon-theme.txt"

FIRST = 0x100000

# An icon is a square one em on a side, sitting where a line of text sits: a
# fifth of it below the baseline. Its advance is the em too, so it is as wide
# as it is tall. That is wider than a terminal cell, on purpose: wezterm draws
# a square glyph across the cell beside it when that cell is a space, and
# scales it down into one cell when it is not.
#
# EVERY icon advances by the em, including the four upstream drew in a box that
# is not square, which nanoemoji would otherwise give a width of their own. A
# set that is one width is a set whose width can be declared once, and a prompt
# that adds up columns needs exactly that.
UPEM = 1000
ASCENDER = 800
DESCENDER = -200

# The font's own timestamps, which would otherwise be the moment of the build.
# 2026-11-01T00:00:00Z; any fixed moment would do.
BUILD_EPOCH = "1793491200"


def fetch_upstream():
    with urllib.request.urlopen(UPSTREAM) as r:
        data = r.read()
    got = hashlib.sha256(data).hexdigest()
    if got != UPSTREAM_SHA256:
        sys.exit(f"{UPSTREAM}\n  sha256 is {got}\n  expected  {UPSTREAM_SHA256}")
    return data


def read_upstream(data):
    """The manifest, each icon's SVG by name, and the license text."""
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        files = {m.name: tar.extractfile(m).read() for m in tar if m.isfile()}
    manifest = json.loads(files["package/dist/material-icons.json"])
    svgs = {}
    for name, definition in manifest["iconDefinitions"].items():
        # "./../icons/rust.svg", relative to dist/.
        path = "package/icons/" + definition["iconPath"].rsplit("/", 1)[1]
        svgs[name] = files[path]
    return manifest, svgs, files["package/LICENSE"]


def build(svgs, codepoints, workdir):
    """Run nanoemoji over the icons and return the font it wrote."""
    staged = workdir / "svg"
    staged.mkdir()
    for name, svg in svgs.items():
        # nanoemoji reads the code point out of the file name.
        (staged / f"emoji_u{codepoints[name]:x}.svg").write_bytes(svg)
    major, minor = (int(part) for part in VERSION.split(".")[:2])
    env = dict(os.environ, SOURCE_DATE_EPOCH=BUILD_EPOCH)
    # nanoemoji drives ninja, which pip installs beside this interpreter.
    env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
    done = subprocess.run(
        [
            sys.executable, "-m", "nanoemoji.nanoemoji",
            "--color_format", "glyf_colr_0",
            "--family", FAMILY,
            "--upem", str(UPEM),
            "--ascender", str(ASCENDER),
            "--descender", str(DESCENDER),
            "--linegap", "0",
            "--width", str(UPEM),
            "--version_major", str(major),
            "--version_minor", str(minor),
            "--output_file", FONT,
            "--build_dir", str(workdir / "build"),
            *sorted(str(p) for p in staged.iterdir()),
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    if done.returncode != 0:
        sys.exit(done.stdout[-4000:] + done.stderr[-4000:])
    return TTFont(workdir / "build" / FONT, recalcTimestamp=False)


def finish(font, license_text):
    """Say whose the icons are, in the font itself.

    The MIT License asks that the copyright notice and the permission notice
    travel with every copy. A font file gets copied on its own, so they are in
    its name table as well as in the file beside it.
    """
    # One width (see UPEM), layers included.
    metrics = font["hmtx"].metrics
    for glyph, (_, lsb) in metrics.items():
        metrics[glyph] = (UPEM, lsb)
    font["post"].isFixedPitch = 1

    # nanoemoji adds a space. The font is named in a fallback chain for its
    # icons, and should answer for nothing else.
    for sub in font["cmap"].tables:
        sub.cmap.pop(0x20, None)

    lines = license_text.splitlines()
    notice = next(line.strip() for line in lines if line.lower().startswith("copyright"))
    names = font["name"]
    for name_id, text in (
        (0, notice),
        (5, f"Version {VERSION}; built by mkicons.py from material-icon-theme {VERSION}"),
        (11, "https://github.com/material-extensions/vscode-material-icon-theme"),
        (13, license_text.strip()),
        (14, "https://opensource.org/license/mit"),
    ):
        names.setName(text, name_id, 3, 1, 0x409)


def table(manifest, codepoints):
    """material-icons.tsv, as text. See THE TABLE above."""
    rows = [("icon", name, f"{cp:x}") for name, cp in codepoints.items()]
    for kind, key in (
        ("ext", "fileExtensions"),
        ("file", "fileNames"),
        ("folder", "folderNames"),
        ("lang", "languageIds"),
    ):
        rows += [(kind, k, icon) for k, icon in manifest[key].items()]
    for what, key in (("file", "file"), ("folder", "folder"), ("root", "rootFolder")):
        rows.append(("default", what, manifest[key]))

    # The rule that lets the open folders be left out. If upstream ever breaks
    # it, this stops the build rather than shipping a table that is wrong.
    opened = dict(manifest["folderNamesExpanded"])
    opened[None] = manifest["folderExpanded"]
    closed = dict(manifest["folderNames"])
    closed[None] = manifest["folder"]
    if opened.keys() != closed.keys() or any(opened[k] != f"{closed[k]}-open" for k in closed):
        sys.exit("an open folder's icon is no longer its closed one's name plus -open")
    if manifest["rootFolderExpanded"] != f"{manifest['rootFolder']}-open":
        sys.exit("the open root folder's icon is no longer the closed one's plus -open")
    for icon in set(closed.values()) | {manifest["rootFolder"]}:
        if f"{icon}-open" not in codepoints:
            sys.exit(f"{icon} has no -open twin")
    for kind, key, icon in rows:
        if kind != "icon" and icon not in codepoints:
            sys.exit(f"{kind} {key!r} names {icon!r}, which is not an icon")
        if any(c in field for field in (key, icon) for c in "\t\n\r"):
            sys.exit(f"{kind} {key!r} cannot be a row of a tab-separated file")
    head = (
        f"# Material Icon Theme {VERSION}: which code point is which icon, and which\n"
        f"# icon a file gets. Written by mkicons.py with {FONT}; see its header\n"
        "# for the columns. Do not edit: regenerate.\n"
    )
    return head + "".join(f"{kind}\t{key}\t{value}\n" for kind, key, value in sorted(rows))


def spellings(name):
    """`name`, and the capitalized ways the same file is written on disk.

    eza matches a name exactly and upstream lists them in lower case, so
    without these a README.md is only its extension and a LICENSE or a
    Makefile is nothing at all. `Name` for anything that starts with a letter,
    and `NAME.ext` when what is before the first dot is all letters: README.md,
    LICENSE, Dockerfile. Upstream's own spelling is always first.
    """
    out = [name]
    if name[:1].islower():
        out.append(name[0].upper() + name[1:])
        stem, dot, rest = name.partition(".")
        if stem.isalpha():
            out.append(stem.upper() + dot + rest)
    return out


def eza_theme(manifest, codepoints):
    """eza/theme.yml, as text. See THE EZA THEME above."""
    def glyph(icon):
        return chr(codepoints[icon])

    # Lowest claim first, so that a later one overwrites it: a spelling this
    # script made up never displaces one upstream wrote down, and a file's
    # icon wins a name it shares with a folder.
    names = {}
    for table in (manifest["folderNames"], manifest["fileNames"]):
        # A folder association can be a path (`.github/workflows`), which is
        # never the name of anything eza lists.
        own = {k: icon for k, icon in table.items() if "/" not in k}
        for k, icon in own.items():
            for spelling in spellings(k)[1:]:
                names.setdefault(spelling, glyph(icon))
        for k, icon in own.items():
            names[k] = glyph(icon)

    # eza lowers a file's extension before it looks, and takes only what is
    # after the last dot.
    extensions = {
        k.lower(): glyph(icon)
        for k, icon in manifest["fileExtensions"].items()
        if "." not in k
    }

    def block(title, entries):
        # JSON's strings are YAML's double-quoted ones, and quoting every key
        # is what lets `.gitignore`, `#recycle` and `404.html` be keys at all.
        rows = "".join(
            f"  {json.dumps(k, ensure_ascii=False)}: "
            f"{{icon: {{glyph: {json.dumps(v, ensure_ascii=False)}}}}}\n"
            for k, v in sorted(entries.items())
        )
        return f"{title}:\n{rows}"

    head = (
        f"# Material Icon Theme {VERSION} for eza: the icon a name or an extension gets.\n"
        f"# Written by mkicons.py from the same release as {FONT}; see its\n"
        "# header for what eza cannot be told. Do not edit: regenerate.\n"
    )
    return head + block("filenames", names) + block("extensions", extensions)


def main():
    if sys.argv[1:]:
        sys.exit(__doc__.strip().splitlines()[2].strip())
    manifest, svgs, license_bytes = read_upstream(fetch_upstream())
    codepoints = {name: FIRST + i for i, name in enumerate(sorted(svgs))}
    outdir = Path(__file__).parent

    with tempfile.TemporaryDirectory() as tmp:
        font = build(svgs, codepoints, Path(tmp))
        drawn = set(font.getBestCmap())
        missing = [name for name, cp in codepoints.items() if cp not in drawn]
        if missing:
            sys.exit(f"{len(missing)} icons did not make it into the font: {missing[:8]}")
        finish(font, license_bytes.decode())
        font.save(outdir / FONT)

    (outdir / TABLE).write_text(table(manifest, codepoints))
    (outdir / EZA).parent.mkdir(exist_ok=True)
    (outdir / EZA).write_text(eza_theme(manifest, codepoints))
    (outdir / LICENSE).write_bytes(license_bytes)
    last = FIRST + len(codepoints) - 1
    print(f"  {FONT:24s} {len(codepoints)} icons, U+{FIRST:X} to U+{last:X}")
    print(f"  {TABLE:24s} {sum(1 for _ in open(outdir / TABLE)) - 3} rows")
    print(f"  {EZA:24s} {sum(1 for _ in open(outdir / EZA)) - 5} names and extensions")


if __name__ == "__main__":
    main()
