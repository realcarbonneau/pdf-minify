# Contextual help and tooltip convention

## Rulings (verbatim)

Exact designer text from `DESIGNER_VERBATIM.md`. Text outside the fenced
quotes is not the designer's.

**§253** (2026-10-17)

```text
Remove the text under Brotli, put that in a tooltip please, plan a standard tooltip as per modern GUI best practices
```

**§252** (2026-10-17)

```text
Mark that option as "(Compatibility)" for clarity.
```

This is the shared convention for new or updated help in the Qt Widgets
application; existing controls are not rewritten all at once.

## Presentation and content

- Use native `QWidget.setToolTip()` / `QAction.setToolTip()` and item-model
  tooltip roles. Keep the platform's font, palette, hover delay and dismissal;
  no custom popup widget, forced duration, animation or hover timer.
- Prefer one concise, plain-language sentence about the control's effect or
  limitation. Do not repeat its label or put a manual in a hover popup.
- Keep the selected option's help current; give combo popup entries their
  own help. Retain useful visible labels and do not hide critical errors or
  required decisions in a tooltip.
- Supply the same short explanation through `accessibleDescription`; provide
  more detailed `whatsThis` help where needed for keyboard Shift+F1 access.
  Longer documentation belongs in developer/user docs, not a larger tooltip.
- Help display/dismissal is view-only: no dirty state, processing, selection,
  saving or artifact changes. Hidden controls must not leave placeholder rows.

## Brotli application

The visible choice remains **Brotli (limited support)**. Its tooltip is:

> Requires a compatible PDF reader; older readers may show missing content.

The declaration checkbox retains **(Compatibility)** in its label. Its short
tooltip explains the option without suggesting it installs decoder support:

> Add Brotli extension metadata for readers that use it; this does not add Brotli decoder support.

More detailed help states that the declaration is off by default and affects
metadata and file size, not image fidelity. The checkbox is also offered for
**Best (Zopfli/Brotli)** (§§255/256), and the declaration is included only if
the chosen output actually uses Brotli; detailed help and the Best recipe
readout state that condition, since a checked setting does not promise Brotli
will win. Best's short help names native/packed-image selection and the
possible reader requirement; it does not claim automatic J* selection. There
is no inline warning label and no space reserved for one.

> Optimize native and packed-image streams; may require a Brotli-capable reader.

## Sources and verification

[Qt QToolTip](https://doc.qt.io/qt-6/qtooltip.html) documents native widget/action
help and normal platform behavior. [KDE inline help guidance](https://develop.kde.org/hig/displaying_content/#inline-help-and-tooltips)
recommends short tooltips and accessible, discoverable detailed help rather
than hover-only essential instructions. The designer chose tooltip placement
for the Brotli help (§253); the visible limited-support label stays.
[QWidget help properties](https://doc.qt.io/qt-6/qwidget.html#accessibleDescription-prop)
provide accessible descriptions and What's This help without extra dependencies.

Test selected/popup help, accessibility text, context changes and no processing
on help events. Capture/view the actual native tooltip and the compact panel
through `tools/shot.py`, including its (Compatibility) control.
