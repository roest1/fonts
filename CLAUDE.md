# CLAUDE.md — fonts

Science Gothic Mono, built by `mkmono.py` and committed, a color icon font built by `mkicons.py` and committed, plus a catalogue of fonts, one file per font in `catalog/`. [roest1/dotfiles](https://github.com/roest1/dotfiles) pins the repo as a submodule at `wezterm/fonts` and links the whole of it to `~/.config/wezterm/fonts`. README.md says how to regenerate the fonts and how to add a catalogue entry. This file holds what it does not.

## Things not to undo

- **The `.ttf` files stay at the repo root.** Three readers look at the top level of the linked directory and no deeper: WezTerm's `font_dirs`, `status_fonts` in dotfiles' `lib/status.sh`, and `fonts::families` in roest1/theme-tui. Moving them means changing all three in the same bump.

- **No font file gets committed that this repo did not build.** WezTerm loads every font file under this directory, and the repo is public, so a committed font is both live in the terminal and redistributed. A font I like is a link in `catalog/`. The two that are built here are Science Gothic Mono and `MaterialIconTheme.ttf`.

- **`mkicons.py`'s packages are pinned by `mkicons.py.lock`, not by its header.** `mkmono.py` has one dependency and pins it inline. nanoemoji brings eighteen of its own, and the bytes depend on all of them, so the header names two and `uv run` reads the lock beside the script for the rest. `uv lock --script mkicons.py --upgrade` moves them, and the regenerated font ships in the same commit.

- **The icon font's timestamps are fixed by `BUILD_EPOCH`.** nanoemoji stamps the font with the time of the build unless `SOURCE_DATE_EPOCH` says otherwise, and two runs a second apart then differ.

- **A code point is not an interface; `material-icons.tsv` is.** Icons are numbered in name order, so a new upstream icon moves every one after it. Whoever draws an icon reads its code point from the table, which is written in the same run and committed in the same change.

- **The icon font answers for its icons and nothing else, and every icon is one width.** `finish` takes out the space nanoemoji adds and sets every advance to the em, including four icons upstream drew in a box that is not square. A set that is one width can have its width declared once, which roest1/PS1 needs to line up its right-hand side.

- **In WezTerm the icon font is named with `assume_emoji_presentation = false`.** WezTerm takes a color font for an emoji font and will not use one for a text code point, which a private-use one is. Named plainly, `wezterm ls-fonts` lists the font as found and `--text` on an icon still says no font has the glyph. That reads as a broken font and is not one.

- **Open folders are left out of the table by rule, and the build checks the rule.** An open folder's icon is its closed one's name plus `-open`. If upstream breaks that, `mkicons.py` stops.

- **The MIT notice is in three places.** `MIT-material-icon-theme.txt` is upstream's file, the font's nameID 0 and 13 carry the copyright and the license text, and `LICENSE` says the icon font is under Material Extensions' copyright and not mine. MIT asks that the notice go with every copy, and a font file gets copied on its own.

- **A refactor of `mkmono.py` that should not change the fonts is proven by running it and getting no diff.** The output is byte for byte reproducible and CI checks it, so a change to the script, its `UPSTREAM` pin or its fontTools pin ships with the regenerated fonts in the same commit.

- **Front matter in `catalog/` is flat `key: value` lines.** `catalog.py` and the awk in `install.sh` read it without a YAML parser, and the `frontMatter()` in roest1/ideas can too. No lists, no quoting, no values that wrap.

- **The OFL notice stays where it is.** `mkmono.py` leaves nameID 0, 13 and 14 alone, `OFL.txt` is upstream's copy from the commit `UPSTREAM` names, and `LICENSE` carves the fonts out of the MIT grant. OFL 1.1 section 5 requires all three to stay true.

- **`ci ok` is the one required check.** Renaming that job blocks every PR.
