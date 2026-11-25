# fonts

**Science Gothic Mono**, a monospaced cut of [Science Gothic](https://github.com/googlefonts/science-gothic) for a terminal grid, plus a catalogue of the fonts I use and a script that installs them.

[roest1/dotfiles](https://github.com/roest1/dotfiles) pins this repo as a submodule at `wezterm/fonts` and links it to `~/.config/wezterm/fonts`. WezTerm reads it there through `font_dirs`. Nothing is installed into the system font path, so no stale copy elsewhere can shadow it.

## Science Gothic Mono

Science Gothic is proportional: its `m` wants 0.99em and its `l` 0.30em. A terminal cell is one fixed width, so the raw font collides and gaps. `mkmono.py` builds each glyph from the width instance (upstream's `wdth` axis, 50–200) whose natural advance lands closest to 0.62em, which is 0xProto's advance. That lets the two fonts share one grid. Only glyphs that overflow even at `wdth=50` get scaled, and only as much as needed. The docstring in `mkmono.py` has the details.

The `.ttf` files are committed. Using them needs no Python, no network and no font tooling. To regenerate them:

```bash
uv run mkmono.py
```

That fetches the upstream release pinned in `mkmono.py` by google/fonts commit and SHA-256. To take a new release, change `UPSTREAM` and `UPSTREAM_SHA256` there, run it, and commit the fonts with the script.

The build is reproducible: the same upstream file and the fontTools version pinned in `mkmono.py` give the same bytes. CI regenerates both cuts and fails if they differ from the committed ones. It also checks that both are fixed-pitch at one advance of 0.62em, that they are named `Science Gothic Mono`, and that the OFL notice is in each file and in `OFL.txt`.

## Material Icon Theme

[Material Icon Theme](https://github.com/material-extensions/vscode-material-icon-theme) is 1256 file and folder icons in color, published as SVG for editors. A terminal draws an icon as a character, so `mkicons.py` builds them into a color font: each icon is a glyph made of flat-colored layers (COLR version 0), which WezTerm draws in color at any size.

- `MaterialIconTheme.ttf`: the icons, at U+100000 to U+1004E7, each one em square.
- `material-icons.tsv`: which code point is which icon, and which icon a file extension, file name or folder name gets. The associations are upstream's own. Read an icon's code point from here; it moves when upstream adds an icon.
- `eza/theme.yml`: the same associations for [eza](https://github.com/eza-community/eza) 0.20 or newer, which cannot read the table. Use it with `EZA_CONFIG_DIR=<this directory>/eza EZA_ICON_SPACING=2`.
- `MIT-material-icon-theme.txt`: upstream's license, which travels with the font.

Fourteen icons use gradients, which this format cannot hold. Each of those becomes one of its colors.

eza takes an icon for a name or an extension and nothing else, so a folder or file with no icon of its own keeps eza's built-in Nerd Font glyph: a listing mixes the two sets. The theme has about 12,000 entries, and eza reads all of them on every run, which measured 16 ms on top of a 2 ms `ls`.

All four files are committed. To regenerate them:

```bash
uv run mkicons.py
```

It takes about two minutes. It fetches the npm release pinned in `mkicons.py` by version and SHA-256, and builds with the packages pinned in `mkicons.py.lock`. To take a new release, change `VERSION` and `UPSTREAM_SHA256`, run it, and commit the four files with the script. To move the packages, run `uv lock --script mkicons.py --upgrade` first.

The build is reproducible, and CI regenerates the files and fails if they differ.

## Fonts I use or like

[`catalog/`](catalog/) has one file per font: where it comes from, what it is for, and what is worth knowing about it. An empty "Used for" means I like the font and have not put it anywhere yet. This table is generated from those files.

<!-- auto:catalog -->
| Font | Tags | Used for | Source | License |
| --- | --- | --- | --- | --- |
| [JetBrainsMono Nerd Font](catalog/jetbrainsmono-nerd-font.md) | editor | the editor lane in nvim | [JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono) | OFL-1.1 |
| [Material Icon Theme](catalog/material-icon-theme.md) | icons |  | [material-extensions/vscode-material-icon-theme](https://github.com/material-extensions/vscode-material-icon-theme) | MIT |
| [0xProto Nerd Font](catalog/0xproto-nerd-font.md) | terminal | the default terminal font | [0xType/0xProto](https://github.com/0xType/0xProto) | OFL-1.1 |
| [IosevkaTerm Nerd Font](catalog/iosevkaterm-nerd-font.md) | terminal | a narrow (0.50em) alternative | [be5invis/Iosevka](https://github.com/be5invis/Iosevka) | OFL-1.1 |
| [Science Gothic Mono](catalog/science-gothic-mono.md) | terminal | `make` output, through SGR 6 | [roest1/fonts](https://github.com/roest1/fonts) | OFL-1.1 |
| [Science Gothic](catalog/science-gothic.md) | ui | the tab bar | [googlefonts/science-gothic](https://github.com/googlefonts/science-gothic) | OFL-1.1 |
<!-- /auto:catalog -->

[Nerd Fonts](https://github.com/ryanoasis/nerd-fonts)' patched fonts keep the source font's OFL. Its scripts are MIT.

### Installing them

```bash
./install.sh '0xProto Nerd Font' 'Science Gothic'
```

`install.sh` takes family names, downloads each from the `download` in its catalogue file, and unpacks it under `~/.local/share/fonts`. It skips a family fontconfig already has. With no arguments it lists what it can install. Science Gothic Mono has no download: it is in this repo, and WezTerm reads it in place. dotfiles' `[wezterm]` section installs the ones its WezTerm config names.

### Adding one

1. Add `catalog/<family-name>.md`, named for the family in lowercase with hyphens. Copy an existing file for the front matter. `tags` says what the font is for (`terminal`, `editor`, `ui`, `web`, ...). `use` and `download` are optional: leave `use` out for a font that is not in use yet, and leave `download` out for a font that is only a link, such as a web font on [Bunny Fonts](https://fonts.bunny.net) or one that is not free to redistribute.
2. Under the front matter, write what is worth knowing about it: its advance, the glyphs it lacks, where it is used.
3. Run `uv run catalog.py`. It checks every file and rewrites the table above. CI fails if the table is stale.

Only the fonts this repo builds are committed here: Science Gothic Mono and Material Icon Theme. Every other font is a link, because WezTerm loads any font file in this directory and because this repo is public.

## License

Science Gothic Mono is OFL-1.1 (`OFL.txt`). The icon font is MIT, under Material Extensions' copyright (`MIT-material-icon-theme.txt`). Everything else is MIT. See [LICENSE](LICENSE).
