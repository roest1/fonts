# fonts

**Science Gothic Mono**, a monospaced cut of [Science Gothic](https://github.com/googlefonts/science-gothic) for a terminal grid, plus a list of the fonts I use.

[roest1/dotfiles](https://github.com/roest1/dotfiles) pins this repo as a submodule at `wezterm/fonts` and links it to `~/.config/wezterm/fonts`. WezTerm reads it there through `font_dirs`. Nothing is installed into the system font path, so no stale copy elsewhere can shadow it.

## Science Gothic Mono

Science Gothic is proportional: its `m` wants 0.99em and its `l` 0.30em. A terminal cell is one fixed width, so the raw font collides and gaps. `mkmono.py` builds each glyph from the width instance (upstream's `wdth` axis, 50–200) whose natural advance lands closest to 0.62em, which is 0xProto's advance. That lets the two fonts share one grid. Only glyphs that overflow even at `wdth=50` get scaled, and only as much as needed. The docstring in `mkmono.py` has the details.

The `.ttf` files are committed. Using them needs no Python, no network and no font tooling. Regenerate them after an upstream release:

```bash
src=$(mktemp)
curl -fsSL -o "$src" 'https://raw.githubusercontent.com/google/fonts/main/ofl/sciencegothic/ScienceGothic%5BCTRS,slnt,wdth,wght%5D.ttf'
uv run mkmono.py "$src" .
```

CI checks that both cuts are fixed-pitch at one advance of 0.62em, that they are named `Science Gothic Mono`, and that the OFL notice is in each file and in `OFL.txt`.

## The fonts I use

| Font | Used for | Source | License |
| --- | --- | --- | --- |
| 0xProto Nerd Font | the default terminal font | [0xType/0xProto](https://github.com/0xType/0xProto), patched by [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts/releases) | OFL-1.1 |
| JetBrainsMono Nerd Font | the editor lane in nvim | [JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono), patched by Nerd Fonts | OFL-1.1 |
| IosevkaTerm Nerd Font | a narrow (0.50em) alternative | [be5invis/Iosevka](https://github.com/be5invis/Iosevka), patched by Nerd Fonts | OFL-1.1 |
| Science Gothic | the tab bar | [googlefonts/science-gothic](https://github.com/googlefonts/science-gothic), via [google/fonts](https://github.com/google/fonts/tree/main/ofl/sciencegothic) | OFL-1.1 |
| Science Gothic Mono | `make` output, through SGR 6 | this repo | OFL-1.1 |

Nerd Fonts' patched fonts keep the source font's OFL. Its scripts are MIT. dotfiles' `[wezterm]` section installs the first four into `~/.local/share/fonts`.

## License

The fonts are OFL-1.1 (`OFL.txt`). Everything else is MIT. See [LICENSE](LICENSE).
