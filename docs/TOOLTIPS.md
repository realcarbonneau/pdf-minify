# Contextual help and tooltip convention

Designer §253; current application: Qt Widgets. This is the shared convention
for new/updated help, not approval to rewrite every existing control at once.

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

More detailed help states that the declaration is off by default, affects
metadata/file size rather than image fidelity. §§255/256 extend availability
to **Best (Zopfli/Brotli)**, with the declaration included only if its selected
output actually uses Brotli. State that condition in detailed help and the
Best recipe readout; a checked setting does not promise Brotli will win.
Best's short help names native/packed-image selection and the possible reader
requirement; it does not claim automatic J* selection. Remove
the former inline warning entirely; do not merely hide an abandoned label.

> Optimize native and packed-image streams; may require a Brotli-capable reader.

## Sources and verification

[Qt QToolTip](https://doc.qt.io/qt-6/qtooltip.html) documents native widget/action
help and normal platform behavior. [KDE inline help guidance](https://develop.kde.org/hig/displaying_content/#inline-help-and-tooltips)
recommends short tooltips and accessible, discoverable detailed help rather
than hover-only essential instructions. This project's designer specifically
chooses tooltip placement for Brotli; the visible limited-support label stays.
[QWidget help properties](https://doc.qt.io/qt-6/qwidget.html#accessibleDescription-prop)
provide accessible descriptions and What's This help without extra dependencies.

Test selected/popup help, accessibility text, context changes and no processing
on help events. Capture/view the actual native tooltip and the compact panel
through `tools/shot.py`, including its (Compatibility) control.
