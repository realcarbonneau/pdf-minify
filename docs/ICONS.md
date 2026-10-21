# Action icons — desktop theme first, one stock fallback

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§114** (2026-10-10)

```text
And put the proper icons on the save, rename, duplicate buttons.
```

**§120** (2026-10-13)

```text
isn't there a standard rename icon that looks like a cursor with a letter or two? Also, remove the text on the filter buttons, rename, copy, save, and just keep the icon and tooltips.
```

**§196** (2026-10-14)

```text
Those icons look odd, in particular the undo and rename, are those standard icons? Standard KDE or nuvola?
```

**§197** (2026-10-14)

```text
ok, as you suggest.
```

**§200** (2026-10-14)

```text
I don't like those icons, make an icon lab menu item with a window with various options and codes for each so I can tell you my choices.  use icons from nuvola, oxygen and other similar libraries.
```

**§294** (2026-10-20)

```text
Also, I want to use the Icon col 5, row 4 from     pdf-minimalist/icons

/test2.png.
```

**§295** (2026-10-20)

```text
Can you put this in the readme?
```

The current icons stay in place until the designer chooses replacements in the
[Icon Lab](ICON_LAB.md) (§200). Work: TODO §201, issue B102.

## Application icon (§§294/295)

The application icon is the designer's choice from `icons/test2.png`: column 5,
row 4, a PDF page pinched into an hourglass by two green arrows. It keeps its
light rounded tile, with transparent corners, padded to a square.
`ui_qt/assets/app_icon/pdf-minify-<size>.png` holds 16, 24, 32, 48, 64, 128 and
256 px versions. `configure_application` sets it as the application's window
and taskbar icon, and the README shows the 128 px version. The action-icon
rules above do not apply to it; it is the product's own artwork.

## Ownership and mappings

`ui_qt/icons.py` is the only action-icon provider; `ActionIcons` binds all
eight main-window actions and both button-lab toolbar pairs to it. Call Qt's
`QIcon.fromTheme` with the matching bundled fallback. Do not override the desktop theme or add
system-dependent absolute asset paths. Both the main window and button lab
use this provider. Standard names:

| Action | Icon name |
|---|---|
| Revert unsaved filter changes | document-revert |
| Rename filter | edit-rename |
| Save As / copy filter | edit-copy |
| Save filter settings; export PDF | document-save |
| Stop export | process-stop |
| Zoom in / out | zoom-in / zoom-out |

Revert restores ALL unsaved filter changes; it is not step-by-step Undo.
Buttons retain their existing callbacks, tooltips, keyboard shortcuts,
enabled state and 20px/16px logical icon sizes. No filtering, timer, saved-file
or selection changes. Native theme/palette changes refresh registered icons
only; Qt owns disabled/active states and HiDPI vector rasterization.

## Portable fallback and licenses

Bundle only the required action SVGs from KDE Breeze, at 16px and 22px source
grids, in light/dark variants. Select the fallback variant for the actual
control/toolbar surface palette, not an assumed window background. Native
styles/stylesheet-polished children can retain a different palette; observe
their own palette changes as well. Do not recolor/retrace glyph paths or
invent replacement artwork. Choose the 16px optical grid for the 16px toolbar
and 22px grid for the existing 20px filter controls; Qt rasterizes the selected
SVG at device scale. Do not add both files to one SVG engine and assume its
per-mode/state SVG slots distinguish source sizes. Pixel tests compare each
fallback with its stock source at both device scales.
The desktop's named icon wins when available. A missing bundled resource is
a packaging error, not permission to return a blank icon or unrelated symbol.

Assets live under `ui_qt/assets/breeze/`; their README records the installed
source snapshot, upstream project, alias resolution and checksums. Retain its
copyright/license notices plus the accompanying LGPL/GPL texts. These are
ordinary package data, not a new Python/system-package dependency. Keep the
SVG icon engine and QtSvg support supplied by PySide6-Essentials in installed
artifacts. No runtime downloads or reliance on this workstation's theme path.
See [PACKAGING.md](PACKAGING.md) and [DEPENDENCIES.md](DEPENDENCIES.md).

## Verification

Tests must cover named-theme precedence, missing theme and individually
missing names, stock fallback provenance, light/dark contrast, transparent
backgrounds, normal/disabled states and 1×/2× rasterization; all action icons
must render nonempty with unchanged logical sizes. Exercise a live palette/
theme refresh without new PDF jobs or changing selection. Capture/view full
windows and 1:1 enabled/disabled controls, both native-theme and forced-
fallback cases.

## References

[Qt QIcon theme/fallback/HiDPI support](https://doc.qt.io/qt-6/qicon.html),
[KDE Breeze](https://invent.kde.org/frameworks/breeze-icons),
[freedesktop icon naming](https://specifications.freedesktop.org/icon-naming/latest/).

## Design traps and failed attempts

- **Hand-drawn glyphs.** Revert and rename were custom 32px QPainter drawings
  that matched no theme (§§196/197). Use named theme icons with the bundled
  Breeze fallback; never draw replacement artwork.
- **Reading a question as a requirement.** §120 asked whether a standard rename
  icon exists; it was implemented as custom artwork instead.
- **Two source sizes in one SVG engine.** Qt's per-mode and state slots do not
  choose between 16px and 22px sources. Pick the grid per control.
