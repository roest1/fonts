---
family: Material Icon Theme
tags: icons
source: https://github.com/material-extensions/vscode-material-icon-theme
license: MIT
---

The color icon font this repo builds. It has no download: `MaterialIconTheme.ttf` is committed at the repo root and WezTerm reads it through `font_dirs`. The [README](../README.md#material-icon-theme) says how it is made.

1256 icons at U+100000 to U+1004E7, each one em square with an advance of one em. It has no letters, so it only makes sense in a fallback chain behind a text font. `material-icons.tsv` says which code point is which icon.

WezTerm has to be told it is not an emoji font: `{ family = "Material Icon Theme", assume_emoji_presentation = false }`. Named plainly it is found and then never used. WezTerm takes any color font for an emoji font, and will not draw a private-use code point, which is text, from one.

An icon is one cell to WezTerm and 1.6 cells wide at 0xProto's 0.62em advance, so it is drawn across the next cell when that cell is a space.
