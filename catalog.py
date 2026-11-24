# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Check catalog/ and write its table into README.md.

    uv run catalog.py            # rewrite the table
    uv run catalog.py --check    # exit 1 if README.md is stale; CI runs this

catalog/ holds one markdown file per font. The front matter is flat
`key: value` lines, so that this script and the awk in install.sh read it the
same way with no YAML parser. roest1/ideas' frontMatter() can parse it too,
though nothing there reads these files yet. The body is free text: what the
font is good at, what it is bad at, where it is used.

    family    the name fontconfig and WezTerm know the font by
    tags      what it is for, comma-separated: terminal, editor, ui, web, ...
    source    the upstream project
    license   the SPDX identifier
    use       optional: one line on where I use it; absent means I only like it
    download  optional: an archive or font file install.sh can fetch
"""
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
README = ROOT / "README.md"
REQUIRED = ("family", "tags", "source", "license")
OPTIONAL = ("use", "download")
UNPACKS = (".tar.xz", ".zip", ".ttf", ".otf")       # the formats install.sh handles
TABLE = re.compile(r"(<!-- auto:catalog -->\n).*?(<!-- /auto:catalog -->)", re.S)


def slug(family):
    return re.sub(r"[^a-z0-9]+", "-", family.lower()).strip("-")


def read(path):
    """One entry's front matter, and what is wrong with it."""
    head = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    if not head:
        return {}, ["no front matter"]
    meta, errors = {}, []
    for line in head[1].splitlines():
        key, sep, value = line.partition(": ")
        # Edge spaces and quotes are where the readers part ways: awk keeps
        # both, ideas drops the quotes. Refusing them keeps one reading.
        if not sep or key in meta or value != value.strip(" \t\"'"):
            errors.append(f"bad or repeated line: {line!r}")
            continue
        meta[key] = value
    errors += [f"missing {k}" for k in REQUIRED if not meta.get(k)]
    errors += [f"unknown key {k}" for k in meta if k not in REQUIRED + OPTIONAL]
    if not re.fullmatch(r"[a-z0-9-]+(, [a-z0-9-]+)*", meta.get("tags", "x")):
        errors.append("tags must be lowercase words separated by ', '")
    for key in ("source", "download"):
        if key in meta and not meta[key].startswith("https://"):
            errors.append(f"{key} is not an https:// URL")
    if "download" in meta and not meta["download"].endswith(UNPACKS):
        errors.append(f"download must end in one of {', '.join(UNPACKS)}")
    # The filename is the family's slug, so one family cannot have two entries
    # and install.sh can name the install directory after the file.
    if "family" in meta and path.stem != slug(meta["family"]):
        errors.append(f"should be named {slug(meta['family'])}.md")
    return meta, errors


def source_label(url):
    u = urlparse(url)
    return u.path.strip("/") if u.netloc == "github.com" else u.netloc


def table(entries):
    rows = ["| Font | Tags | Used for | Source | License |", "| --- | --- | --- | --- | --- |"]
    for path, m in sorted(entries, key=lambda e: (e[1]["tags"], e[1]["family"].lower())):
        rows.append(f"| [{m['family']}](catalog/{path.name}) | {m['tags']} | {m.get('use', '')} "
                    f"| [{source_label(m['source'])}]({m['source']}) | {m['license']} |")
    return "\n".join(rows) + "\n"


def main():
    found = [(path, *read(path)) for path in sorted((ROOT / "catalog").glob("*.md"))]
    errors = [f"catalog/{path.name}: {e}" for path, _, errs in found for e in errs]
    if errors:
        sys.exit("\n".join(errors))
    entries = [(path, meta) for path, meta, _ in found]

    old = README.read_text()
    new, n = TABLE.subn(lambda m: m[1] + table(entries) + m[2], old)
    if n != 1:
        sys.exit("README.md needs exactly one <!-- auto:catalog --> ... <!-- /auto:catalog --> block")
    if new == old:
        return
    if "--check" in sys.argv[1:]:
        sys.exit("README.md's font table is stale. Run: uv run catalog.py")
    README.write_text(new)
    print("README.md: font table rewritten")


if __name__ == "__main__":
    main()
