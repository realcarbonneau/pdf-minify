# Icon Lab — stock alternatives with permanent choice codes

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§200** (2026-10-14)

```text
I don't like those icons, make an icon lab menu item with a window with various options and codes for each so I can tell you my choices.  use icons from nuvola, oxygen and other similar libraries.
```

The lab compares real library icons so the designer can send back choices;
never select a replacement on the designer's behalf. Work: TODO §203, issue
B104.

## Interaction and ownership

View → Icon Lab… is a direct menu action. Open one resizable, modeless window
per main window; reopening raises it and retains that window's choices.
Compare columns Nuvola (N), Oxygen (O), GNOME Classic (G), Breeze (B), with
rows for Revert Changes, Rename Filter, Save As / Copy Filter, Save settings /
export, Stop export, Zoom in and Zoom out. Native scrolling keeps rows/columns
accessible in a small window. The main window's layout is unchanged.

Each candidate displays its permanent code, actual upstream name, real
app-size enabled/disabled controls and an enlarged inspection preview. Use
16px for toolbar actions and 20px for filter actions; enlarged means a 32px
preview, not a claim that a bitmap has extra detail. Preserve stock artwork;
Qt supplies disabled state. Light/dark backgrounds are review controls only.

Codes have the form `N-REV-01`, `O-REN-01`, etc.: family, action and explicit
variant ID, not current row index. Never renumber/reassign an existing code
to different artwork. A new variant gets a new code. Metadata resolves a code
to exact source files/hashes. `document-revert` and `edit-undo` may be visual
alternatives for the SAME Revert Changes action; this does not add history
Undo or change the action's discard-all semantics. Name nonstandard visual
alternatives honestly with the original library glyph name.

One radio group per action lets the designer collect a per-action selection.
A read-only summary and Copy choices button produce a pasteable reply with
action labels and codes. Initially select nothing: no implied endorsement.
Clear choices resets only this review selection, not the background or app.
There is NO Apply button, no settings write, no production-icon update, no
filter edit/selection change and no PDF processing from any lab interaction.
Closing the lab is not an unsaved-filter operation.

## Assets and portability

Bundle a curated, immutable subset, not entire themes. Nuvola comes from the
official Debian archived `nuvola-icon-theme` 15.08.3-2 package (David Vignoni),
Oxygen and GNOME Classic from the installed Debian snapshots, and Breeze
reuses the bundled fallback SVGs. Keep original size variants when
available; do not upscale files on disk or draw replacement glyphs.

The lab loads each requested family directly from bundled resources. It must
not call theme lookup that could show an inherited icon from another family
under a Nuvola/Oxygen label. Retain source URLs/package versions, aliases,
original PNG-byte hashes, copyright notices, Nuvola's artwork addendum and
full license texts. Package the resource data independently of the sibling
Task Coach checkout and `/usr/share/icons`; no runtime download/install.
`assets/icon_lab/` holds lossless base64 PNG resource data (decoded in memory),
its provenance manifest and notices; Breeze SVGs stay under `assets/breeze/`.
See [ICONS.md](ICONS.md) and [PACKAGING.md](PACKAGING.md).

## Verification

Test code uniqueness and fixed meanings, genuine family/resource ownership,
checksums, available PNG dimensions, nonblank normal/disabled/HiDPI rendering,
radio exclusivity per action, copyable summary, no implicit initial choices,
window reuse and no application-action/settings/filter/job mutations. Use
`tools/shot.py` to capture/view the actual lab at normal/2×, light/dark,
selected/disabled states and narrow-window scrolling, including 1:1 crops,
following the shared verification rules in `DEVELOPER_GUIDELINES.md`. Selection codes are not permission to
infer unmentioned production changes. Paint-fixture choices are not designer
choices and are never applied to the app.
