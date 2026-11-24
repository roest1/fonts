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

## Fonts I use or like

[`catalog/`](catalog/) has one file per font: where it comes from, what it is for, and what is worth knowing about it. An empty "Used for" means I like the font and have not put it anywhere yet. This table is generated from those files.

<!-- auto:catalog -->
| Font | Tags | Used for | Source | License |
| --- | --- | --- | --- | --- |
| [JetBrainsMono Nerd Font](catalog/jetbrainsmono-nerd-font.md) | editor | the editor lane in nvim | [JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono) | OFL-1.1 |
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

Only Science Gothic Mono's files are committed here. Every other font is a link, because WezTerm loads any font file in this directory and because this repo is public.

## License

The fonts are OFL-1.1 (`OFL.txt`). Everything else is MIT. See [LICENSE](LICENSE).
