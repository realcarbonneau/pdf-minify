"""The stock-icon comparison is portable, coded, and deliberately non-applying."""
import base64
import hashlib
import json
import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QSize, Qt  # noqa: E402
from PySide6.QtGui import QIcon, QImage  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minify.ui_qt.icon_lab import (  # noqa: E402
    ACTIONS, ASSET_ROOT, BY_CODE, CANDIDATES, FAMILIES, IconLab,
    candidate_icon, resource_bank,
)

_app = QApplication.instance() or QApplication([])


@pytest.fixture
def lab():
    window = IconLab()
    window.show()
    _app.processEvents()
    yield window
    window.close()
    window.deleteLater()
    _app.processEvents()


def test_catalog_permanent_codes_and_complete_action_family_matrix():
    assert len(BY_CODE) == len(CANDIDATES) == 37
    assert dict(FAMILIES) == {"N": "Nuvola", "O": "Oxygen", "G": "GNOME Classic", "B": "Breeze"}
    for action in ACTIONS:
        for family, _ in FAMILIES:
            assert any(c.action == action.key and c.family == family for c in CANDIDATES)
    # Exact code meanings used in the designer's copy/pasted reply. New
    # candidates must get new codes rather than renumbering these originals.
    expected = {
        "N": {"REV": ["document-revert", "edit-undo"], "REN": ["edit"],
              "COP": ["edit-copy", "document-save-as"], "SAV": ["document-save"],
              "STP": ["process-stop", "dialog-cancel"], "ZIN": ["zoom-in"], "ZOU": ["zoom-out"]},
        "O": {"REV": ["document-revert", "edit-undo"], "REN": ["edit-rename", "document-edit"],
              "COP": ["edit-copy", "document-save-as"], "SAV": ["document-save"],
              "STP": ["process-stop", "dialog-cancel"], "ZIN": ["zoom-in"], "ZOU": ["zoom-out"]},
        "G": {"REV": ["document-revert", "edit-undo"], "REN": ["insert-text"],
              "COP": ["edit-copy", "document-save-as"], "SAV": ["document-save"],
              "STP": ["process-stop"], "ZIN": ["zoom-in"], "ZOU": ["zoom-out"]},
        "B": {"REV": ["document-revert"], "REN": ["edit-rename"],
              "COP": ["edit-copy"], "SAV": ["document-save"], "STP": ["process-stop"],
              "ZIN": ["zoom-in"], "ZOU": ["zoom-out"]},
    }
    for family, actions in expected.items():
        for action, names in actions.items():
            for variant, name in enumerate(names, 1):
                assert BY_CODE[f"{family}-{action}-{variant:02d}"].name == name


def test_original_png_hashes_dimensions_license_notices_and_no_orphan_data():
    bank = resource_bank()
    assert set(bank) == {f"{c.family}/{c.name}" for c in CANDIDATES if c.family != "B"}
    count = 0
    for key, sources in bank.items():
        assert {16, 32} <= {source["size"] for source in sources}, key
        for source in sources:
            raw = base64.b64decode(source["png"], validate=True)
            assert hashlib.sha256(raw).hexdigest() == source["sha256"]
            image = QImage.fromData(raw, "PNG")
            assert not image.isNull()
            assert image.size() == QSize(source["size"], source["size"])
            count += 1
    assert count == 121
    manifest = json.loads((ASSET_ROOT / "manifest.json").read_text())
    assert {key: value["name"] for key, value in manifest["families"].items()} == dict(FAMILIES)
    for family in ("Nuvola", "Oxygen", "GNOME"):
        assert (ASSET_ROOT / f"COPYRIGHT.{family}").is_file()
    assert "NOTE THIS ADD-ON" in (ASSET_ROOT / "NOTICE.Nuvola.upstream.txt").read_text()
    assert "GNU LESSER GENERAL PUBLIC LICENSE" in (ASSET_ROOT / "LICENSE.LGPL-2.1").read_text()
    assert "GNU GENERAL PUBLIC LICENSE" in (ASSET_ROOT / "LICENSE.GPL-2").read_text()


@pytest.mark.parametrize("candidate", CANDIDATES, ids=lambda c: c.code)
def test_all_choices_render_normal_disabled_and_hidpi_without_theme(candidate, monkeypatch):
    monkeypatch.setattr(QIcon, "fromTheme", lambda *a, **kw: pytest.fail("family lookup must not use themes"))
    window = IconLab()
    try:
        for background in (1, 2):
            window.background.setCurrentIndex(background)
            for size in (16, 20, 32):
                icon = candidate_icon(candidate, window.palette(), size)
                for dpr in (1., 2.):
                    for mode in (QIcon.Normal, QIcon.Disabled):
                        pixmap = icon.pixmap(QSize(size, size), dpr, mode)
                        assert not pixmap.isNull()
                        # Stock raster packs may have only 48px for a 64px
                        # request; QIcon preserves the logical extent/DPR.
                        assert abs(pixmap.deviceIndependentSize().width()-size) <= 1
                        image = pixmap.toImage().convertToFormat(QImage.Format_RGBA8888)
                        alpha = bytes(image.constBits())[3::4]
                        # Genuine stock shadows can leave alpha=1 in scaled
                        # corners. Preserve those samples, not a hard cutoff.
                        assert max(alpha) > 0 and min(alpha) < 255
    finally:
        window.deleteLater()
        _app.processEvents()


def test_groups_summary_preview_click_and_copy_are_review_only(lab):
    assert not lab.isModal()
    assert not lab.choice_text() and not lab.summary.toPlainText()
    assert lab.summary.isReadOnly() and not lab.copy_button.isEnabled()
    assert all(group.checkedButton() is None for group in lab.groups.values())
    radio = lab.choices["N-REV-02"]
    QTest.mouseClick(radio, Qt.LeftButton, pos=QPoint(8, radio.height()//2))
    assert lab.choices["N-REV-02"].isChecked()
    radio = lab.choices["O-REV-01"]
    QTest.mouseClick(radio, Qt.LeftButton, pos=QPoint(8, radio.height()//2))
    assert lab.choices["O-REV-01"].isChecked() and not lab.choices["N-REV-02"].isChecked()
    lab.previews["O-REN-01"][0].click()
    text = "Revert Changes: O-REV-01\nRename Filter: O-REN-01"
    assert lab.choice_text() == lab.summary.toPlainText() == text
    assert lab.copy_button.isEnabled()
    old_clipboard = QApplication.clipboard().text()
    try:
        lab.copy_button.click()
        assert QApplication.clipboard().text() == text
    finally:
        QApplication.clipboard().setText(old_clipboard)
    for background in (2, 1, 0):
        lab.background.setCurrentIndex(background)
        assert lab.choice_text() == text
    assert not any(button.text() == "Apply" for button in lab.findChildren(type(lab.copy_button)))


def test_clear_choices_resets_only_the_review_selection(lab):
    assert not lab.clear_button.isEnabled()
    lab.choices["N-REV-02"].setChecked(True)
    lab.choices["O-REN-01"].setChecked(True)
    lab.background.setCurrentIndex(2)
    assert lab.clear_button.isEnabled()
    lab.clear_button.click()
    assert all(group.checkedButton() is None and group.exclusive()
               for group in lab.groups.values())
    assert not lab.choice_text() and not lab.summary.toPlainText()
    assert not lab.copy_button.isEnabled() and not lab.clear_button.isEnabled()
    assert lab.background.currentIndex() == 2
    lab.choices["O-REV-01"].setChecked(True)
    assert lab.copy_button.isEnabled() and lab.clear_button.isEnabled()


def test_small_window_scrolls_all_choices_and_keyboard_can_select(lab):
    lab.resize(640, 520)
    _app.processEvents()
    assert lab.table.horizontalScrollBar().maximum() > 0
    assert lab.table.verticalScrollBar().maximum() > 0
    for column in range(lab.table.columnCount()):
        assert lab.table.columnWidth(column) >= 178
    lab.table.verticalScrollBar().setValue(0)
    radio = lab.choices["N-REV-01"]
    radio.setFocus()
    QTest.keyClick(radio, Qt.Key_Space)
    assert lab.groups["REV"].checkedButton() is radio
    lab.table.verticalScrollBar().setValue(lab.table.verticalScrollBar().maximum())
    lab.table.horizontalScrollBar().setValue(lab.table.horizontalScrollBar().maximum())
    _app.processEvents()
    assert lab.choices["B-ZOU-01"].visibleRegion().boundingRect().width() > 0
