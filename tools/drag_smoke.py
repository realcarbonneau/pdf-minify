"""Exercise native filter drags under X11 and capture their rendered ghosts.

Usage: xvfb-run -a ./.venv/bin/python tools/drag_smoke.py
Requires xdotool. Settings are isolated; artifacts go to .tmp/drag-*.png.
"""
import os
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QPoint, QRect, QTimer, Qt, QSettings  # noqa: E402
from PySide6.QtGui import QFont, QImage, QPainter, QPalette, QPixmap  # noqa: E402
from PySide6.QtWidgets import QApplication, QAbstractItemView, QMessageBox, QStyle, QStyleOptionViewItem  # noqa: E402

from pdf_minify.ui_qt.app import MainWindow, setup_logging, STRIP_ICON, FILTER_UUID_ROLE  # noqa: E402
from pdf_minify.core import presets  # noqa: E402
from pdf_minify.core.identity import new_filter_uuid  # noqa: E402


def main():
    with tempfile.TemporaryDirectory(prefix="pdfmin-drag-settings-") as config:
        os.environ["XDG_CONFIG_HOME"] = config
        setup_logging()
        app = QApplication([])
        # Match the designer's 11-filter shape, including a saved FFPR copy.
        custom = copy.deepcopy(presets.get("bw-t210"))
        custom.update(id="smoke-forced-copy", uuid=new_filter_uuid(),
                      label="BW · Strong T=210 FFPR")
        custom["params"]["force_raster"] = True
        settings = QSettings("pdf-minify", "pdf-minify")
        settings.setValue("customPresets", [custom])
        settings.setValue("stripOrder", ["smoke-forced-copy", "bw-t180", "bw-otsu",
                          "bw-fast", "bw-t210", "color-p16", "color-i64",
                          "bw-sauvola", "color-j2k", "color-max", "color-bal"])
        w = MainWindow(str(ROOT / "examples/images.pdf"))
        w.resize(1100, 650)
        w.move(20, 20)
        w.show()
        v = w.filters
        artifact_dir = ROOT / ".tmp"
        artifact_dir.mkdir(exist_ok=True)
        scale = w.devicePixelRatioF()
        artifact_prefix = "drag" if scale == 1 else f"drag-{scale:g}x"
        errors = []
        started = time.monotonic()
        scenarios = iter(("strip", "above", "controls", "below", "escape",
                          "tail-8", "tail-last", "tail-repeat"))
        original_uuids = {v.item(i).data(FILTER_UUID_ROLE) for i in range(v.count())}

        def xdotool(*args):
            subprocess.run(["xdotool", *map(str, args)], check=True, timeout=5)

        def move_cursor(global_pos, press=False):
            # Qt uses logical coordinates; Xvfb's X11 root uses physical
            # coordinates. This harness runs on one screen at origin (0,0).
            # --sync waits for actual movement and hangs when successive
            # scrolled cells occupy the same physical position. X request
            # ordering plus the scheduled Qt verification gives our barrier.
            args = ["mousemove", round(global_pos.x() * scale),
                    round(global_pos.y() * scale)]
            if press:
                args.extend(("mousedown", 1))
            xdotool(*args)

        def fail(exc):
            errors.append(str(exc))
            xdotool("mouseup", 1, "key", "Escape")
            # This harness owns isolated settings/artifacts; failed dirty-state
            # checks must not leave an unattended modal blocking test cleanup.
            w._ask_unsaved_filter = lambda pid: "discard"
            w.close()
            app.quit()

        def checked(callback):
            def run():
                try:
                    callback()
                except Exception as exc:
                    traceback.print_exc()
                    fail(exc)
            return run

        def check_model(expected, generation, artifacts):
            assert v.count() == len(expected) == len(original_uuids), "native drag lost/duplicated a row"
            assert [v.item(i).data(Qt.UserRole) for i in range(v.count())] == expected
            assert {v.item(i).data(FILTER_UUID_ROLE) for i in range(v.count())} == original_uuids
            assert w._strip_ids == expected
            assert [w.preset.itemData(i) for i in range(w.preset.count())] == expected
            assert v.state() == QAbstractItemView.NoState, "Qt's stale drag gesture is still armed"
            assert w._gen == generation and not w._artifacts.pending, "click/reorder reprocessed a filter"
            assert w._artifacts.results == artifacts, "click/reorder replaced a prepared result"

        def verify_visible_numbers(name):
            # Read the actual X11 window, not QWidget.grab() (which forces a
            # fresh paint). The normal post-drop paint must already be correct.
            image = w.screen().grabWindow(int(w.winId())).toImage().convertToFormat(
                QImage.Format_ARGB32)
            image.save(str(artifact_dir / f"{artifact_prefix}-drop-{name}.png"))
            dpr = image.devicePixelRatio()
            strip_pos = v.viewport().mapTo(w, QPoint())
            image.copy(QRect(round(strip_pos.x() * dpr), round(strip_pos.y() * dpr),
                             round(v.viewport().width() * dpr),
                             round(v.viewport().height() * dpr))).save(
                str(artifact_dir / f"{artifact_prefix}-drop-strip-{name}.png"))
            checked_rows = 0
            for row in range(v.count()):
                rect = v.visualRect(v.model().index(row, 0))
                if not v.viewport().rect().contains(rect):
                    continue
                # Compare the first native frame to a fresh paint of CURRENT
                # model state, without repainting the real viewport. Use the
                # actual delegate/options, not a second font/layout renderer.
                expected = QPixmap(image.size())
                expected.setDevicePixelRatio(dpr)
                expected.fill(v.palette().color(QPalette.Base))
                pt = QPainter(expected)
                pt.translate(strip_pos)
                pid = v.item(row).data(Qt.UserRole)
                label = w._strip_label(pid)
                assert w.preset.itemText(row) == label, (name, row, "combo number")
                option = QStyleOptionViewItem()
                v.initViewItemOption(option)
                option.rect = rect
                if v.item(row).isSelected():
                    option.state |= QStyle.State_Selected
                else:
                    option.state &= ~QStyle.State_Selected
                v.itemDelegate().paint(pt, option, v.model().index(row, 0))
                pt.end()
                origin = v.viewport().mapTo(w, rect.topLeft() + QPoint(0, 116))
                actual_rect = QRect(round(origin.x() * dpr), round(origin.y() * dpr),
                                    round(150 * dpr), round(13 * dpr))
                actual_caption = image.copy(actual_rect)
                expected_caption = expected.toImage().convertToFormat(
                    QImage.Format_ARGB32).copy(actual_rect)
                if actual_caption != expected_caption:
                    # Keep the first normal frame intact; diagnostic crops
                    # must not force a QWidget repaint and hide a stale frame.
                    prefix = artifact_dir / f"{artifact_prefix}-caption-{name}-{row}"
                    actual_caption.save(f"{prefix}-actual.png")
                    expected_caption.save(f"{prefix}-expected.png")
                    raise AssertionError((name, row, pid, label, "native caption pixel mismatch",
                                          actual_rect.getRect(), v.horizontalScrollBar().value()))
                checked_rows += 1
            assert checked_rows >= 4, (name, "not enough complete visible captions")

        def next_drag():
            if (len(w._mini_view) < len(w._strip_ids)
                    or len(w._mini_amount) < len(w._strip_ids)
                    or w._artifacts.pending):
                assert time.monotonic() - started < 90, "filter jobs timed out"
                QTimer.singleShot(100, checked(next_drag))
                return
            name = next(scenarios, None)
            if name is None:
                verify_dirty_cancel_and_revert()
                return
            original = list(w._strip_ids)
            generation, artifacts = w._gen, dict(w._artifacts.results)
            xdotool("windowfocus", int(w.winId()))
            row = (v.count() - 1 if name == "tail-last" else 8) if name.startswith("tail-") else 1
            v.scrollToItem(v.item(row))
            app.processEvents()
            rect = v.visualRect(v.model().index(row, 0))
            press = rect.center()
            if name == "controls":
                global_target = w.preset.mapToGlobal(w.preset.rect().center())
                target = v.viewport().mapFromGlobal(global_target)
            else:
                x = v.visualRect(v.model().index(3, 0)).right() + 1
                y = rect.center().y() if name.startswith("tail-") else {
                    "strip": rect.center().y(), "above": -170,
                    "below": v.viewport().height() + 22, "escape": -170}[name]
                target = QPoint(x, y)
                global_target = v.viewport().mapToGlobal(target)
            gap = v._gap_at(target.x())
            global_press = v.viewport().mapToGlobal(press)
            move_cursor(global_press, press=True)
            before = None
            base = None
            released_at = None

            def capture_source():
                nonlocal before, base
                assert v.currentRow() == row
                assert v._press is not None, (name, "native single press did not arrive")
                pixmap = v._drag_base_pixmap(row)
                pixmap.save(str(artifact_dir / f"{artifact_prefix}-source-{name}.png"))
                base = pixmap.toImage()
                assert v.viewport().height() == rect.height(), name
                assert v.verticalScrollBar().maximum() == 0, name
                assert base.pixelColor(5, base.height() - 1) == base.pixelColor(5, 5), (
                    name, "neutral bottom bar in source")
                before = w.grab().toImage()
                # Exercise Qt's sub-threshold DraggingState first. The former
                # parallel manual controller left that state armed after exec.
                move_cursor(v.viewport().mapToGlobal(press + QPoint(1, 0)))

            def cross_threshold():
                move_cursor(v.viewport().mapToGlobal(press + QPoint(25, 0)))

            def move_to_target():
                move_cursor(global_target)

            def capture_drag():
                assert v._drag_row == row, f"{name}: native drag did not start"
                assert v._drop_gap == gap, f"{name}: target gap differs"
                assert v._drag_ghost.isVisible(), f"{name}: ghost disappeared"
                assert v._drop_line.isVisible(), f"{name}: insertion bar disappeared"
                expected_pos = target - (press - rect.topLeft())
                assert v._drag_overlay_pos == expected_pos, f"{name}: grab point moved"
                image = w.grab().toImage().convertToFormat(QImage.Format_ARGB32)
                image.save(str(artifact_dir / f"{artifact_prefix}-{name}.png"))
                # Verify both the upper margin and the previously clipped
                # bottom margin, using physical pixels on high-DPI displays.
                dpr = base.devicePixelRatio()
                for local in (QPoint(5, 5), QPoint(5, rect.height() - 3)):
                    sample = v._drag_ghost.pos() + local
                    if not w.rect().contains(sample):
                        continue  # the below-window portion is naturally clipped
                    source = base.pixelColor(round(local.x() * dpr), round(local.y() * dpr))
                    dest_dpr = image.devicePixelRatio()
                    physical = QPoint(round(sample.x() * dest_dpr), round(sample.y() * dest_dpr))
                    destination = before.pixelColor(physical)
                    actual = image.pixelColor(physical)
                    for channel in ("red", "green", "blue"):
                        expected = round(getattr(source, channel)() * 0.75
                                         + getattr(destination, channel)() * 0.25)
                        assert abs(getattr(actual, channel)() - expected) <= 2, (
                            name, local, channel, actual.getRgb(), expected)

            def release():
                nonlocal released_at
                released_at = time.monotonic()
                if name == "escape":
                    xdotool("key", "Escape", "mouseup", 1)
                else:
                    xdotool("mouseup", 1)

            def verify_drop():
                # X11 completes the drop asynchronously. Wait for its
                # completion event instead of assuming a fixed timer delay,
                # particularly when rendering large high-DPI captures.
                if v._drag_row is not None:
                    assert time.monotonic() - released_at < 3, (
                        name, "native drag did not finish after release")
                    QTimer.singleShot(50, checked(verify_drop))
                    return
                expected = list(original)
                if name != "escape":
                    moved = expected.pop(row)
                    dst = gap - 1 if gap > row else gap
                    expected.insert(dst, moved)
                    assert w.preset.currentData() == original[row], name
                    assert v.currentRow() == dst, (
                        name, "selection", v.currentRow(), dst, w._strip_ids, expected)
                check_model(expected, generation, artifacts)
                assert v._drag_row is None and v._drag_ghost is None, (
                    name, "drag did not finish", v._drag_row)
                assert v._drop_line.isHidden(), (name, "insertion bar stayed visible")
                verify_visible_numbers(name)
                print(f"PASS native drag: {name}, gap={gap}, visible numbering", flush=True)
                if name.startswith("tail-"):
                    verify_clicks_after_move(expected, generation, artifacts, name)
                else:
                    QTimer.singleShot(100, checked(next_drag))

            QTimer.singleShot(100, checked(capture_source))
            QTimer.singleShot(175, checked(cross_threshold))
            QTimer.singleShot(250, checked(move_to_target))
            QTimer.singleShot(500, checked(capture_drag))
            QTimer.singleShot(750, checked(release))
            QTimer.singleShot(1000, checked(verify_drop))

        def verify_clicks_after_move(expected, generation, artifacts, name):
            rows = iter(range(v.count()))

            def click_next():
                row = next(rows, None)
                if row is None:
                    print(f"PASS native clicks: {name}, every mini UUID/caption stable", flush=True)
                    # The next scenario may press this same last cell. It is
                    # an independent drag, not a double-click-and-drag: allow
                    # the platform's click classification interval to expire.
                    QTimer.singleShot(app.doubleClickInterval()+50, checked(next_drag))
                    return
                v.scrollToItem(v.item(row))
                app.processEvents()
                rect = v.visualRect(v.model().index(row, 0))
                move_cursor(v.viewport().mapToGlobal(rect.center()))  # plain hover must not start another drag
                xdotool("mousedown", 1, "mouseup", 1)

                def verify_click():
                    check_model(expected, generation, artifacts)
                    assert w._active_pid == expected[row]
                    assert v._drag_row is None and v._drag_ghost is None
                    verify_visible_numbers(f"{name}-click-{row + 1}")
                    QTimer.singleShot(20, checked(click_next))

                QTimer.singleShot(100, checked(verify_click))

            QTimer.singleShot(100, checked(click_next))

        def verify_dirty_cancel_and_revert():
            """§§160–162: actual X11 mini click, Escape, then Revert button."""
            edited = "bw-t180"
            v.setCurrentRow(w._strip_ids.index(edited))
            saved = w._artifacts.results[w._result_key(edited)]
            w.slider.setValue(203)

            def click_when_ready():
                if w._preview_timer.isActive() or w._artifacts.pending:
                    QTimer.singleShot(100, checked(click_when_ready))
                    return
                live = w._artifacts.results[w._result_key(edited)]
                generation, results = w._gen, dict(w._artifacts.results)
                order = list(w._strip_ids)
                v.scrollToItem(v.item(w._strip_ids.index("bw-otsu")))
                app.processEvents()
                target = v.visualItemRect(v.item(w._strip_ids.index("bw-otsu"))).center()
                move_cursor(v.viewport().mapToGlobal(target))
                xdotool("mousedown", 1, "mouseup", 1)

                def escape_prompt():
                    box = app.activeModalWidget()
                    assert isinstance(box, QMessageBox), "native dirty mini click did not show its dialog"
                    assert box.button(QMessageBox.Discard).text() == "Discard Changes"
                    box.screen().grabWindow(int(box.winId())).save(
                        str(artifact_dir / f"{artifact_prefix}-filter-unsaved-dialog.png"))
                    xdotool("windowfocus", int(box.winId()), "key", "Escape")
                    # Xvfb has no window manager to return focus from a closed
                    # modal. Drive that normal desktop step explicitly before
                    # comparing active-theme caption pixels.
                    QTimer.singleShot(60, checked(lambda: xdotool("windowfocus", int(w.winId()))))
                    QTimer.singleShot(180, checked(after_cancel))

                def after_cancel():
                    check_model(order, generation, results)
                    assert w._active_pid == w.preset.currentData() == edited
                    assert [item.data(Qt.UserRole) for item in v.selectedItems()] == [edited]
                    assert v.currentItem().data(Qt.UserRole) == edited and v._press is None
                    assert w._shown_preview_key == w._result_key(edited) and w.slider.value() == 203
                    assert edited in w._draft_specs and w.isWindowModified()
                    assert Path(saved.pdf_path).is_file() and Path(live.pdf_path).is_file()
                    verify_visible_numbers("dirty-cancel")
                    assert w.revert_btn.isEnabled()
                    move_cursor(w.revert_btn.mapToGlobal(w.revert_btn.rect().center()))
                    xdotool("mousedown", 1, "mouseup", 1)
                    QTimer.singleShot(150, checked(after_revert))

                def after_revert():
                    assert w._gen == generation and not w._artifacts.pending
                    assert w._active_pid == w.preset.currentData() == edited
                    assert [item.data(Qt.UserRole) for item in v.selectedItems()] == [edited]
                    assert not w._draft_specs and not w.isWindowModified()
                    assert w.slider.value() == 180 and not w.revert_btn.isEnabled()
                    assert w._artifacts.results[w._result_key(edited)] is saved
                    assert Path(saved.pdf_path).is_file() and not Path(live.pdf_path).exists()
                    verify_visible_numbers("reverted")
                    print("PASS native dirty mini Escape and Revert Changes: selection/files retained correctly", flush=True)
                    w.close()
                    app.quit()

                QTimer.singleShot(150, checked(escape_prompt))

            QTimer.singleShot(100, checked(click_when_ready))

        QTimer.singleShot(100, checked(next_drag))
        QTimer.singleShot(100000, lambda: fail(RuntimeError("native drag smoke timed out")))
        old_hook = sys.excepthook

        def qt_exception(exc_type, value, tb):
            traceback.print_exception(exc_type, value, tb)
            fail(value)  # Qt slot failures must fail the smoke, not just print

        sys.excepthook = qt_exception
        try:
            app.exec()
        finally:
            sys.excepthook = old_hook
        if errors:
            print("FAIL:", *errors, sep="\n", file=sys.stderr)
            return 1
        print("NATIVE DRAG SMOKE GREEN", flush=True)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
