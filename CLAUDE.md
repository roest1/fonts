# CLAUDE.md — fonts

Science Gothic Mono, built by `mkmono.py` and committed, plus a catalogue of fonts, one file per font in `catalog/`. [roest1/dotfiles](https://github.com/roest1/dotfiles) pins the repo as a submodule at `wezterm/fonts` and links the whole of it to `~/.config/wezterm/fonts`. README.md says how to regenerate the fonts and how to add a catalogue entry. This file holds what it does not.

## Things not to undo

- **The `.ttf` files stay at the repo root.** Three readers look at the top level of the linked directory and no deeper: WezTerm's `font_dirs`, `status_fonts` in dotfiles' `lib/status.sh`, and `fonts::families` in roest1/theme-tui. Moving them means changing all three in the same bump.

- **No other font file gets committed.** WezTerm loads every font file under this directory, and the repo is public, so a committed font is both live in the terminal and redistributed. A font I like is a link in `catalog/`.

- **A refactor of `mkmono.py` that should not change the fonts is proven by running it and getting no diff.** The output is byte for byte reproducible and CI checks it, so a change to the script, its `UPSTREAM` pin or its fontTools pin ships with the regenerated fonts in the same commit.

- **Front matter in `catalog/` is flat `key: value` lines.** `catalog.py` and the awk in `install.sh` read it without a YAML parser, and the `frontMatter()` in roest1/ideas can too. No lists, no quoting, no values that wrap.

- **The OFL notice stays where it is.** `mkmono.py` leaves nameID 0, 13 and 14 alone, `OFL.txt` is upstream's copy from the commit `UPSTREAM` names, and `LICENSE` carves the fonts out of the MIT grant. OFL 1.1 section 5 requires all three to stay true.

- **`ci ok` is the one required check.** Renaming that job blocks every PR.
