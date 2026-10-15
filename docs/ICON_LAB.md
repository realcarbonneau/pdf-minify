# Icon Lab — stock alternatives with permanent choice codes

Designer ruling §200, 2026-10-14 (America/New_York); TODO §203, issue B104.
The designer rejects the current appearance and asks to compare real library
icons, then communicate their choices. §197's provider implementation is not
acceptance of those particular glyphs. Do not select a replacement on the
designer's behalf.

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
reuses the previously bundled SVG sources. Keep original size variants when
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
selected/disabled states and narrow-window scrolling, including 1:1 crops.
Run the full regression suite and follow the shared developer verification
rules in `DEVELOPER_GUIDELINES.md`. Only explicit designer confirmation
closes the issue; selection codes themselves are not permission to infer
unmentioned production changes.

## Implemented evidence — 2026-10-14

37 permanent choices cover seven action rows and four families, including
curved-arrow/page-revert, copy/Save As and stop/cancel visual alternatives.
121 original PNG size variants cover 30 distinct Nuvola/Oxygen/GNOME glyphs;
seven existing Breeze SVG glyphs complete the matrix. Resource data is 268KB
before git compression, not whole theme bundles. Package/hash provenance
and unmodified notices/licenses are in `assets/icon_lab/`; no pip/apt package
was installed. `tests/test_icon_lab.py` pins every initial code meaning,
stock hashes/dimensions, family-specific loading without theme inheritance,
normal/disabled/HiDPI rendering, radio/copy/clear/keyboard/scroll behavior.
The main-window regression additionally proves direct menu access, one-window
reuse, retained review choices and no production-icon/settings/filter/job
mutation. Full suite: **382 passed in 78.93s**. Focused cases: **43 passed**
at 100% (3.72s) and 2× (4.37s).

`tools/shot.py --icon-lab-only` passed at both scales, using the actual menu
dialog, no PDF processing. Unselected, light/dark selected fixtures, lower
rows, 640×520 top and bottom-right scrolling and 1:1 code/icon cards were
actually viewed. Paint-fixture choices are not designer choices and were
never applied to the app. Runtime/version evidence is recorded in
`PLATFORMS.md`; B104 remains OPEN for designer acceptance.
