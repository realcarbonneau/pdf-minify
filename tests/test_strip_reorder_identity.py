"""Designer §§156/157: one drag controller and model-owned strip identity."""

import os
import copy
import pytest
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, QTimer, Qt, QSettings, QMimeData, QRect
from PySide6.QtGui import QDrag, QMouseEvent, QDropEvent, QDragEnterEvent, QPixmap, QPainter, QFont, QPalette
from PySide6.QtWidgets import QApplication, QAbstractItemView

from pdf_minimalist.ui_qt.app import MainWindow, _StripList, STRIP_ICON, FILTER_UUID_ROLE, FILTER_DRAG_MIME
from pdf_minimalist.core import presets

_app = QApplication.instance() or QApplication([])
_defaults = copy.deepcopy(presets.PRESETS)


@pytest.fixture
def window(monkeypatch):
    settings = QSettings("pdf-minimalist", "pdf-minimalist")
    kept = {key: settings.value(key) for key in settings.allKeys()}
    previous = copy.deepcopy(presets.PRESETS)
    settings.clear()
    presets.PRESETS[:] = copy.deepcopy(_defaults)
    w = MainWindow()
    w.show()
    _app.processEvents()
    yield w
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "discard")
    w.close()
    presets.PRESETS[:] = previous
    settings.clear()
    for key, value in kept.items():
        settings.setValue(key, value)


def test_qt_drag_initiation_has_no_second_default_controller():
    # QDrag consumes release in its nested native loop. The old separate
    # controller cleared its _press while Qt still held a pressed index.
    # A subsequent move could then fall into Qt's unoverridden startDrag.
    assert "startDrag" in _StripList.__dict__, "Qt's default copy/remove path is still active"


def test_native_threshold_owns_and_clears_qt_gesture_state(window):
    w = window
    v = w.filters
    press = v.visualRect(v.model().index(1, 0)).center()

    def send(kind, point, button, buttons):
        event = QMouseEvent(kind, QPointF(point),
                            QPointF(v.viewport().mapToGlobal(point)),
                            button, buttons, Qt.NoModifier)
        _app.sendEvent(v.viewport(), event)

    try:
        send(QEvent.MouseButtonPress, press, Qt.LeftButton, Qt.LeftButton)
        send(QEvent.MouseMove, press + QPoint(1, 0), Qt.NoButton, Qt.LeftButton)
        assert v.state() == QAbstractItemView.DraggingState
        QTimer.singleShot(50, QDrag.cancel)
        send(QEvent.MouseMove, press + QPoint(40, 0), Qt.NoButton, Qt.LeftButton)
        # The old independent mouseMove controller left Qt in DraggingState;
        # the next plain hover could start the DEFAULT drag, with row removal.
        assert v.state() == QAbstractItemView.NoState, "custom drag left Qt's old pressed gesture armed"
        assert v._press is None and v._drag_row is None
        send(QEvent.MouseMove, press + QPoint(60, 0), Qt.NoButton, Qt.NoButton)
        assert v.state() == QAbstractItemView.NoState and v.count() == len(w._strip_ids)
    finally:
        send(QEvent.MouseButtonRelease, press, Qt.LeftButton, Qt.NoButton)
        w.close()


def test_model_is_the_only_order_not_a_mutable_shadow_array(window):
    original = window._strip_ids
    detached = window._strip_ids
    detached.reverse()
    assert window._strip_ids == original
    assert "_strip_ids" not in window.__dict__


def test_repeated_high_index_moves_and_all_clicks_preserve_every_identity(window, monkeypatch):
    w, v = window, window.filters
    original = {v.item(i).data(FILTER_UUID_ROLE): v.item(i) for i in range(v.count())}
    expected = w._strip_ids
    for pid in expected:
        w._paint_strip_item(pid)  # prepared-content layout, not the no-document placeholder
    icons = {uid: item.icon().cacheKey() for uid, item in original.items()}

    def forbidden(*args):
        pytest.fail("reorder/click must not refresh content or filter the document")
    monkeypatch.setattr(w, "_paint_strip_item", forbidden)
    monkeypatch.setattr(w, "_dispatch_filters", forbidden)

    for src, gap in ((8, 4), (9, 1), (1, 10), (7, 5), (5, 0), (8, 3)):
        v.setCurrentRow(src)
        pid = expected.pop(src)
        dst = gap - 1 if gap > src else gap
        expected.insert(dst, pid)
        assert v._move_to_gap(gap)
        assert v.count() == len(original)
        assert w._strip_ids == expected
        assert [w.preset.itemData(i) for i in range(w.preset.count())] == expected
        assert {v.item(i).data(FILTER_UUID_ROLE): v.item(i) for i in range(v.count())} == original
        for row, pid in enumerate(expected):
            v.setCurrentRow(row)
            v.scrollToItem(v.item(row))
            _app.processEvents()
            assert w._active_pid == pid and w.preset.currentData() == pid
            assert v.item(row).text() == presets.get(pid)["label"]
            assert w.preset.itemText(row) == f"{row + 1}. {presets.get(pid)['label']}"
            rect = v.visualRect(v.model().index(row, 0))
            visible = rect.intersected(v.viewport().rect())
            assert visible.width() >= 148  # Qt EnsureVisible may leave a 1px edge clipped
            expected_image = QPixmap(*STRIP_ICON)
            expected_image.fill(v.palette().color(QPalette.Base))
            pt = QPainter(expected_image)
            font = QFont(v.font())
            font.setPointSize(max(7, font.pointSize() - 2))
            pt.setFont(font)
            pt.setPen(v.palette().color(QPalette.WindowText))
            pt.drawText(QRect(0, 116, 150, 13), Qt.AlignHCenter,
                        f"{row + 1}. {presets.get(pid)['label']}")
            wash = v.palette().color(QPalette.Highlight)
            wash.setAlphaF(0.35)
            pt.fillRect(expected_image.rect(), wash)
            pt.end()
            caption = QRect(max(0, -rect.x()), 116, visible.width(), 13)
            actual = v.viewport().grab(rect).toImage()
            assert actual.copy(caption) == expected_image.toImage().copy(caption), (src, gap, row, pid)
        assert {uid: item.icon().cacheKey() for uid, item in original.items()} == icons


def test_drag_payload_has_only_uuid_and_foreign_model_data_cannot_insert(window):
    v = window.filters
    ids = window._strip_ids
    v._begin_drag(0, v.visualRect(v.model().index(0, 0)).center())
    try:
        assert v._drag_mime.formats() == [FILTER_DRAG_MIME]
        assert bytes(v._drag_mime.data(FILTER_DRAG_MIME)).decode() == presets.get(ids[0])["uuid"]
        for payload in (v.model().mimeData([v.model().index(0, 0)]), QMimeData()):
            # Even a UUID copied from our active drag is not a second source.
            if not payload.formats():
                payload.setData(FILTER_DRAG_MIME, v._drag_mime.data(FILTER_DRAG_MIME))
            enter = QDragEnterEvent(QPointF(600, 50), Qt.MoveAction, payload,
                                   Qt.LeftButton, Qt.NoModifier)
            v.dragEnterEvent(enter)
            assert not enter.isAccepted()
            drop = QDropEvent(QPointF(600, 50), Qt.MoveAction, payload,
                             Qt.LeftButton, Qt.NoModifier)
            v.dropEvent(drop)
            assert not drop.isAccepted()
            assert window._strip_ids == ids and v.count() == len(ids)
    finally:
        v._end_drag()


def test_duplicate_persisted_order_cannot_create_duplicate_uuid_items(window):
    ids = window._strip_ids
    window._custom_store().setValue("stripOrder", [ids[2], ids[2], "unknown", ids[0], ids[0]])
    assert window._apply_strip_order(ids) == [ids[2], ids[0], *[p for p in ids if p not in (ids[2], ids[0])]]


def test_content_updates_find_uuid_item_not_old_row(window):
    w, v = window, window.filters
    target = w._strip_ids[8]
    uid = presets.get(target)["uuid"]
    for pid in w._strip_ids:
        w._paint_strip_item(pid)
    v.setCurrentRow(8)
    assert v._move_to_gap(4)
    items = {v.item(i).data(FILTER_UUID_ROLE): v.item(i) for i in range(v.count())}
    before = {key: item.icon().cacheKey() for key, item in items.items()}
    w._filter_prog[target] = 0.5
    w._paint_strip_item(target)
    after = {key: item.icon().cacheKey() for key, item in items.items()}
    assert {key for key in before if before[key] != after[key]} == {uid}
