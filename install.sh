#!/usr/bin/env bash
# Install fonts from the catalogue, by family name:
#
#     ./install.sh '0xProto Nerd Font' 'Science Gothic'
#     ./install.sh                      # list what can be installed
#
# The caller says which fonts it wants; catalog/ says where each one comes
# from. A family fontconfig already knows is left alone, so this is safe to run
# on every install. Files go to $XDG_DATA_HOME/fonts/<entry name>/, whole
# archive, because the license inside it has to travel with the font.
#
# Exit status: 0 when every family is there, 1 when a download or install
# failed, 2 when the catalogue cannot provide a family that was asked for. A
# failed download usually costs looks, not function, so a caller may shrug at 1.
# It should not shrug at 2: that is a misspelled name, and it will not fix itself.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"

# field <file> <key>: one front-matter value. catalog.py holds the format to
# flat `key: value` lines so that this is all the parsing it takes.
field() {
  awk -v key="$2: " '
    NR > 1 && $0 == "---" { exit }
    index($0, key) == 1 { print substr($0, length(key) + 1); exit }
  ' "$1"
}

# No grep -q: under pipefail it exits at the first match, fc-list can die of
# SIGPIPE mid-write, and the pipeline then reports failure for a font that is
# there.
installed() {
  fc-list --format '%{family}\n' | tr ',' '\n' | grep -Fx -- "$1" >/dev/null
}

# fetch <url> <dir>: download and unpack. The formats are catalog.py's UNPACKS.
fetch() {
  local url="$1" dir="$2" tmp="$TMP/download"
  curl -fsSL -o "$tmp" "$url" || return 1
  mkdir -p "$dir"
  case "$url" in
    *.tar.xz) tar -xJf "$tmp" -C "$dir" ;;
    *.zip) unzip -o -q "$tmp" -d "$dir" ;;
    *.ttf | *.otf) cp "$tmp" "$dir/$(basename "$dir").${url##*.}" ;;
    *) return 1 ;;
  esac
}

# warn <status> <message>: say it, and keep the worst status seen.
warn() {
  echo "  ⚠️  $2"
  [ "$status" -ge "$1" ] || status="$1"
}

if [ $# -eq 0 ]; then
  echo "usage: install.sh <family>..."
  echo "installable:"
  for file in "$HERE"/catalog/*.md; do
    [ -n "$(field "$file" download)" ] && echo "  $(field "$file" family)"
  done
  exit 0
fi

if ! command -v fc-list >/dev/null 2>&1; then
  echo "  fontconfig is not installed, so nothing here renders fonts — skipping"
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

status=0
for family in "$@"; do
  entry=""
  for file in "$HERE"/catalog/*.md; do
    [ "$(field "$file" family)" = "$family" ] && { entry="$file"; break; }
  done
  if [ -z "$entry" ]; then
    warn 2 "$family is not in the catalogue"
    continue
  fi
  if installed "$family"; then
    echo "  ✅ $family (already installed)"
    continue
  fi
  url="$(field "$entry" download)"
  if [ -z "$url" ]; then
    warn 2 "$family has no download in the catalogue"
    continue
  fi

  dir="$DEST/$(basename "$entry" .md)"
  echo "  installing $family → ${dir/#$HOME/\~}"
  # The last check is the one that matters: fontconfig now answers to the name
  # the catalogue gave, which is the name every config will ask for.
  if fetch "$url" "$dir" && fc-cache -f "$dir" && installed "$family"; then
    echo "  ✅ $family"
  else
    warn 1 "$family did not install from $url"
  fi
done
exit "$status"
