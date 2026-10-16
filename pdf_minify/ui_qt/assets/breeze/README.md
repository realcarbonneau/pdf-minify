# Stock KDE Breeze action icons

Only the seven used action names are bundled, at 16/22px source grids and
in Breeze / Breeze Dark variants. These are stock SVGs from Debian package
`breeze-icon-theme` **4:5.116.0-1**, copied on 2026-10-14; no artwork was
redrawn or recolored. Line endings are normalized to LF; all SVG content is
otherwise unchanged.

Upstream: https://invent.kde.org/frameworks/breeze-icons
Mirror: https://github.com/KDE/breeze-icons
Installed source: `/usr/share/icons/{breeze,breeze-dark}/actions/{16,22}/`.
`edit-rename.svg` resolves to the upstream `document-edit.svg` alias (a pencil);
other aliases, exact source paths and bundled SHA-256 hashes are recorded in
[manifest.json](manifest.json). Source paths are provenance, never runtime lookup.

Copyright: **2014, Uri Herrera <uri_herrera@nitrux.in>**.
License: **GNU LGPL version 3 or later**, as specified for the icon files by
the source package's [COPYRIGHT](COPYRIGHT) (retained verbatim).
Full [LGPL-3](LICENSE.LGPL-3) and its incorporated [GPL-3](LICENSE.GPL-3)
license texts accompany the assets. The source package's COPYRIGHT also
describes other files not included in this subset; it is not a claim that
every listed license applies to these SVGs.

Keep the SVGs, manifest, this notice and license texts in packaged artifacts.
`ui_qt/icons.py` prefers the user's desktop icon theme and uses these files
only as the matched portable fallback. No KDE/theme package installation or
runtime network access is required. See [the icon design](../../../../docs/ICONS.md)
and [packaging plan](../../../../docs/PACKAGING.md).
