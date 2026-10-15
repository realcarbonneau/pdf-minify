"""Offscreen review of the real-file and unsaved-filter GUI (§149)."""

import os
from pathlib import Path
import sys
import tempfile
import time

for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(var, "1")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QTimer, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox  # noqa: E402
from pdf_minimalist.ui_qt.app import MainWindow, setup_logging  # noqa: E402


def main():
    with tempfile.TemporaryDirectory(prefix="pdfmin-filter-review-settings-") as config:
        os.environ["XDG_CONFIG_HOME"] = config
        setup_logging()
        app = QApplication([])
        w = MainWindow(str(ROOT / "examples/images.pdf"))
        w.resize(1100, 650)
        w.show()
        out = ROOT / ".tmp"
        out.mkdir(exist_ok=True)

        def wait_ready():
            deadline = time.monotonic() + 90
            while w._artifacts.pending or w._preview_timer.isActive():
                assert time.monotonic() < deadline, "filter processing did not finish"
                app.processEvents()
                time.sleep(0.02)
            app.processEvents()
            assert not w._artifacts.errors, w._artifacts.errors

        wait_ready()
        generation = w._gen
        for pid in w._strip_ids:
            w.preset.setCurrentIndex(w.preset.findData(pid))
            assert not w._artifacts.pending and not w._preview_timer.isActive()
            assert w._shown_preview_key == w._result_key(pid)
            artifact = w._artifacts.results[w._result_key(pid)]
            assert w._mini_amount[pid] == w._sized(Path(artifact.pdf_path).stat().st_size)
        assert w._gen == generation, "first visits caused processing"
        w.preset.setCurrentIndex(w.preset.findData("bw-t180"))
        app.processEvents()
        w.grab().save(str(out / "filter-saved.png"))
        saved = w._artifacts.results[w._result_key("bw-t180")]
        w.slider.setValue(203)
        wait_ready()
        live = w._artifacts.results[w._result_key("bw-t180")]
        assert w.preset.currentText().endswith(" *")
        assert Path(saved.pdf_path).exists() and Path(live.pdf_path).exists()
        w.grab().save(str(out / "filter-dirty.png"))
        strip = w.filters.viewport().grab()
        strip.save(str(out / "filter-dirty-strip.png"))
        errors = []

        def review_actual_name():
            dialog = app.activeModalWidget()
            try:
                assert isinstance(dialog, QInputDialog)
                editor = dialog.findChild(QLineEdit)
                editor.selectAll()
                QTest.keyClicks(editor, "Palette review copy")
                dialog.grab().save(str(out / "filter-save-as-name-dialog.png"))
                QTest.keyClick(dialog, Qt.Key_Return)
            except Exception as exc:
                errors.append(str(exc))
                if dialog is not None:
                    dialog.reject()

        def review_actual_prompt(action):
            box = app.activeModalWidget()
            try:
                assert isinstance(box, QMessageBox)
                name = {"discard": "filter-unsaved-dialog.png",
                        "escape": "filter-unsaved-cancel-dialog.png",
                        "save_as": "filter-save-as-switch-dialog.png"}[action]
                box.grab().save(str(out / name))
                assert box.button(QMessageBox.Discard).text() == "Discard Changes"
                if action == "escape":
                    QTest.keyClick(box, Qt.Key_Escape)
                elif action == "save_as":
                    button = next(b for b in box.buttons() if b.text() == "Save As…")
                    QTimer.singleShot(100, review_actual_name)
                    QTest.mouseClick(button, Qt.LeftButton)
                else:
                    QTest.mouseClick(box.button(QMessageBox.Discard), Qt.LeftButton)
            except Exception as exc:
                errors.append(str(exc))
                if box is not None:
                    box.reject()

        def click_other_mini(action):
            v = w.filters
            target = v.item(w._strip_ids.index("bw-otsu"))
            v.scrollToItem(target)
            app.processEvents()
            QTimer.singleShot(100, lambda: review_actual_prompt(action))
            QTest.mouseClick(v.viewport(), Qt.LeftButton, Qt.NoModifier,
                             v.visualItemRect(target).center())
            app.processEvents()
            assert not errors, errors

        generation = w._gen
        click_other_mini("escape")
        assert w._active_pid == w.preset.currentData() == "bw-t180"
        assert [item.data(Qt.UserRole) for item in w.filters.selectedItems()] == ["bw-t180"]
        assert "bw-t180" in w._draft_specs and w.slider.value() == 203
        assert Path(saved.pdf_path).exists() and Path(live.pdf_path).exists()
        assert w._gen == generation and not w._artifacts.pending
        w.grab().save(str(out / "filter-after-cancel.png"))
        assert w.revert_btn.isEnabled()
        w.revert_btn.grab().save(str(out / "filter-revert-icon.png"))
        QTest.mouseClick(w.revert_btn, Qt.LeftButton)
        app.processEvents()
        assert not w._draft_specs and not w.revert_btn.isEnabled()
        assert w._active_pid == "bw-t180" and w.slider.value() == 180
        assert w._artifacts.results[w._result_key("bw-t180")] is saved
        assert w._gen == generation and not w._artifacts.pending
        assert Path(saved.pdf_path).exists() and not Path(live.pdf_path).exists()
        w.grab().save(str(out / "filter-after-revert.png"))

        w.slider.setValue(203)
        wait_ready()
        live = w._artifacts.results[w._result_key("bw-t180")]
        click_other_mini("discard")
        assert not errors, errors
        assert not w._draft_specs
        assert w._active_pid == "bw-otsu"
        assert Path(saved.pdf_path).exists() and not Path(live.pdf_path).exists()
        w.grab().save(str(out / "filter-after-discard.png"))

        # §183: spinner, slider and typed palette values feed ONE timer and
        # publish the completed file for the final value, not intermediate jobs.
        w.preset.setCurrentIndex(w.preset.findData("color-p16"))
        submitted, start = [], w._artifacts.start
        def count_start(key, path, spec, executor):
            worker = start(key, path, spec, executor)
            if worker is not None and not worker.is_copy:
                submitted.append(spec.copy())
            return worker
        w._artifacts.start = count_start
        for _ in range(3):
            w.colors_value.stepDown()
            QTest.qWait(35)
        w.colors.setValue(8)
        w.colors_value.selectAll()
        QTest.keyClicks(w.colors_value, "3")
        QTest.qWait(220)
        assert w._preview_timer.isActive() and not submitted
        wait_ready()
        assert len(submitted) == 1 and submitted[0]["colors"] == 3
        assert w._shown_preview_key == w._result_key("color-p16")
        w.grab().save(str(out / "filter-palette-spinner-3.png"))
        w.after.viewport().grab().save(str(out / "filter-palette-spinner-3-preview.png"))
        w.revert_filter()
        assert not w._draft_specs and len(submitted) == 1
        w.grab().save(str(out / "filter-palette-reverted-16.png"))

        # §189: the real mini-click prompt and nested native naming dialog
        # must select the new copy, not continue to the clicked BW filter.
        original = w._artifacts.results[w._result_key("color-p16")]
        before_ids = set(w._strip_ids)
        w.colors_value.setValue(4)
        wait_ready()
        live = w._artifacts.results[w._result_key("color-p16")]
        generation, real_submissions = w._gen, len(submitted)
        click_other_mini("save_as")
        wait_ready()
        nid, = set(w._strip_ids)-before_ids
        assert w._active_pid == w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == nid
        assert [i.data(Qt.UserRole) for i in w.filters.selectedItems()] == [nid]
        assert w.colors_value.value() == 4 and not w._draft_specs and not w.isWindowModified()
        assert w._shown_preview_key == w._result_key(nid)
        copy = w._artifacts.results[w._result_key(nid)]
        assert copy.nbytes == live.nbytes and Path(copy.pdf_path).is_file()
        assert Path(original.pdf_path).is_file() and w._saved_specs["color-p16"]["colors"] == 16
        assert w._gen == generation and len(submitted) == real_submissions
        w.grab().save(str(out / "filter-save-as-selected.png"))
        w.filters.viewport().grab().save(str(out / "filter-save-as-selected-strip.png"))
        print("FILTER LIFECYCLE GUI SMOKE GREEN", flush=True)
        w.close()
        deadline = time.monotonic() + 10
        while w._jobs:
            assert time.monotonic() < deadline
            app.processEvents()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
