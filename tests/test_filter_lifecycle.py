"""Canon §§32/37/44/48/53/55/90/108/122/149: one real file, explicit edits."""

import copy
from concurrent.futures import Future
import os
from pathlib import Path
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pymupdf as fitz
import numpy as np
import pytest
from PySide6.QtCore import QModelIndex, QSettings, QTimer, Qt, QEvent
from PySide6.QtGui import QHelpEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QFileDialog, QInputDialog, QMessageBox, QToolTip

from pdf_minify.core import presets, pipeline
from pdf_minify.core.recipes import preset_spec, spec_key
from pdf_minify.core.display import render_display_page
from pdf_minify.ui_qt import app as ui
from pdf_minify.ui_qt.artifacts import build_artifact
from pdf_minify.ui_qt.artifacts import ArtifactStore
from pdf_minify.ui_qt.paths import sweep_stale_temps

_app = QApplication.instance() or QApplication([])
_defaults = copy.deepcopy(presets.PRESETS)


def wait_until(condition, timeout=40):
    deadline = time.monotonic() + timeout
    while not condition():
        assert time.monotonic() < deadline, "condition did not settle"
        _app.processEvents()
        time.sleep(0.01)
    _app.processEvents()


@pytest.fixture
def window(tmp_path, monkeypatch):
    previous = copy.deepcopy(presets.PRESETS)
    settings = QSettings("pdf-minify", "pdf-minify")
    kept = {key: settings.value(key) for key in settings.allKeys()}
    settings.clear()
    presets.PRESETS[:] = copy.deepcopy(_defaults)
    source = tmp_path / "three.pdf"
    with fitz.open() as doc:
        for i in range(3):
            page = doc.new_page(width=240, height=240)
            page.insert_text((20, 80), f"Actual saved file, page {i + 1}")
            page.draw_rect(fitz.Rect(20, 100, 120, 180), color=(1, 0, 0))
        doc.save(source)
    w = ui.MainWindow(str(source))
    w.resize(1100, 650)
    w.show()
    try:
        wait_until(lambda: not w._artifacts.pending and
                   len(w._mini_amount) == len(w._strip_ids))
    except AssertionError:
        # Name the filters that failed in the background, with their errors.
        raise AssertionError(f"filters did not finish: {w._artifacts.errors}") from None
    yield w
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "discard")
    w.close()
    wait_until(lambda: not w._jobs)
    presets.PRESETS[:] = previous
    settings.clear()
    for key, value in kept.items():
        settings.setValue(key, value)


def choose(w, pid):
    w.preset.setCurrentIndex(w.preset.findData(pid))
    assert w._active_pid == pid


def request_filter(w, pid, entry):
    """A native selection request may resolve to a Save As destination."""
    if entry == "dropdown":
        w.preset.setCurrentIndex(w.preset.findData(pid))
    elif entry == "mini":
        target = w.filters.item(w._strip_ids.index(pid))
        w.filters.scrollToItem(target)
        QTest.mouseClick(w.filters.viewport(), Qt.LeftButton, Qt.NoModifier,
                         w.filters.visualItemRect(target).center())
    else:
        assert w._strip_ids.index(pid) == w.filters.currentRow()+1
        w.filters.setFocus()
        QTest.keyClick(w.filters, Qt.Key_Right)


def edit(w, value=203):
    choose(w, "bw-t180")
    w.slider.setValue(value)
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert w._active_pid in w._draft_specs
    return w._artifacts.results[w._result_key(w._active_pid)]


def test_every_filter_has_one_real_file_and_exact_full_size(window):
    w = window
    assert len(w._artifacts.results) == len({w._result_key(pid) for pid in w._strip_ids})
    for pid in w._strip_ids:
        result = w._artifacts.results[w._result_key(pid)]
        directory = Path(result.directory)
        assert directory.parent.name == presets.get(pid)["uuid"]
        assert directory.parent.parent.name == str(os.getpid())
        assert not any(p.name.startswith("session-") for p in directory.parents)
        assert result.nbytes == os.path.getsize(result.pdf_path)
        assert w._mini_amount[pid] == w._sized(result.nbytes)
        assert len(result.pages) == 3 and len(result.mini_pages) == 3
        with fitz.open(result.pdf_path) as doc:
            for i, page in enumerate(doc):
                pix = render_display_page(page, dpi=150)
                pixels = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                    pix.height, pix.width, 3)
                assert np.array_equal(result.pages[i], pixels), (pid, i)


def test_first_visits_views_and_reorder_start_no_work(window, monkeypatch):
    w = window
    generation = w._gen
    results = dict(w._artifacts.results)
    seen = []

    def forbidden(*args, **kwargs):
        pytest.fail("selection/view/reorder must never submit processing work")

    monkeypatch.setattr(w._artifacts, "start", forbidden)
    monkeypatch.setattr(w, "_ask_unsaved_filter", forbidden)
    for pid in list(w._strip_ids):
        choose(w, pid)
        seen.append(pid)
        assert w._shown_preview_key == w._result_key(pid)
        assert w.after._pdf_source.path == w._artifacts.results[w._result_key(pid)].pdf_path
        assert w.before._pdf_source.path == w.path
        assert not w._preview_timer.isActive()
        assert not w._draft_specs
        assert not w.status.text().startswith("Rendering")
    for pane, zoom in ((w.before, 0.05), (w.after, 0.35),
                       (w.before, 1.0), (w.after, 2.0)):
        pane.set_zoom(zoom)
        _app.processEvents()
        w._reframe_minis()
        assert w.before.cols() == w.after.cols() == w._current_view()[0]
        assert w.before.sceneRect() == w.after.sceneRect()
        assert [w.before.page_pos(i) for i in range(3)] == [w.after.page_pos(i) for i in range(3)]
        if zoom == 0.05:
            assert w.before.cols() == 3
            for view in (w.before, w.after):
                center = view.mapFromScene(view.sceneRect().center())
                assert abs(center.x() - view.viewport().rect().center().x()) <= 2
                assert abs(center.y() - view.viewport().rect().center().y()) <= 2
        w.before.goto_page(2)
    assert w.filters.model().moveRow(QModelIndex(), 0, QModelIndex(), 4)
    _app.processEvents()
    assert len(seen) == len(w._strip_ids)
    assert w._gen == generation and not w._artifacts.pending
    assert w._artifacts.results == results


def test_displayed_draft_file_is_owned_until_native_view_releases_it(window):
    w = window
    previous = edit(w, 203)
    old_source = w.after._pdf_source
    w.slider.setValue(204)
    assert w._preview_timer.isActive()
    assert Path(previous.pdf_path).exists()
    assert old_source.doc is not None
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert w.after._pdf_source is not old_source
    assert old_source.doc is None
    assert not Path(previous.pdf_path).exists()
    assert Path(w.after._pdf_source.path).exists()


def test_typed_threshold_commits_one_recipe_and_revert_syncs_both(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    starts, start = [], w._artifacts.start
    def count(*args, **kwargs):
        worker = start(*args, **kwargs)
        if worker is not None:
            starts.append(args[0])
        return worker
    monkeypatch.setattr(w._artifacts, "start", count)
    number = w.threshold_value
    number.setFocus()
    number.selectAll()
    QTest.keyClicks(number, "203")
    assert w.slider.value() == 203 and w._draft_specs["bw-t180"]["t"] == 203
    assert w._preview_timer.isActive()
    QTest.keyClick(number, Qt.Key_Return)
    assert w.slider.value() == number.value() == 203
    assert w._draft_specs["bw-t180"]["t"] == 203
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1
    w.revert_filter()
    assert number.value() == w.slider.value() == 180
    assert not w._draft_specs and len(starts) == 1
    choose(w, "color-i64")
    assert w.colors_value.value() == w.colors.value() == 64
    assert w.colors_value.isEnabled() and not w.threshold_value.isEnabled()


def test_live_edit_debounces_one_recipe_and_marks_dirty(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    original = w._saved_specs["bw-t180"].copy()
    starts, start = [], w._artifacts.start

    def count(*args, **kwargs):
        worker = start(*args, **kwargs)
        if worker is not None:
            starts.append(args[0])
        return worker

    monkeypatch.setattr(w._artifacts, "start", count)
    for value in (201, 202, 203):
        w.slider.setValue(value)
    assert w._preview_timer.isActive() and not starts
    assert w._strip_label("bw-t180").endswith(" *")
    assert w.preset.currentText().endswith(" *")
    assert w.afterHeader.property("fullText").startswith(w._filter_display_name("bw-t180") + " · ")
    assert w.filters.currentItem().text().endswith(" *")
    assert w.isWindowModified()
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1
    assert w._saved_specs["bw-t180"] == original
    assert w._draft_specs["bw-t180"]["t"] == 203


def test_reverting_controls_reuses_saved_result_without_work(window):
    w = window
    choose(w, "bw-t180")
    saved = w._artifacts.results[w._result_key("bw-t180")]
    generation = w._gen
    w.slider.setValue(203)
    w.slider.setValue(180)
    assert not w._draft_specs and not w._preview_timer.isActive()
    assert not w.isWindowModified()
    assert w._artifacts.results[w._result_key("bw-t180")] is saved
    assert w._gen == generation and not w._artifacts.pending


def test_mixed_controls_restart_one_global_trailing_timer_and_publish_latest(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    timer = w._preview_timer
    assert timer.interval() == ui.FILTER_EDIT_DEBOUNCE_MS == 300
    assert timer.isSingleShot() and timer.timerType() == Qt.PreciseTimer
    starts, start = [], w._artifacts.start
    def count(key, path, spec, executor):
        worker = start(key, path, spec, executor)
        if worker is not None:
            starts.append((key, spec.copy(), time.monotonic()))
        return worker
    monkeypatch.setattr(w._artifacts, "start", count)
    actions = [lambda: w.threshold_value.stepUp(),
               lambda: w.slider.setValue(202),
               lambda: w.dpi.setCurrentIndex(w.dpi.findData(150)),
               lambda: w.force_raster.setChecked(True),
               lambda: w.page_size.setCurrentIndex(w.page_size.findData("letter"))]
    for action in actions:
        action()
        assert w._preview_timer is timer and timer.isActive()
        assert w.isWindowModified()
        QTest.qWait(80)
        assert not starts
    last_edit = time.monotonic() - .080
    QTest.qWait(150)  # total 230ms since the final input: MUST still be waiting
    assert timer.isActive() and not starts
    wanted = w._result_key(w._active_pid)
    wait_until(lambda: not timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1 and starts[0][0] == wanted
    assert starts[0][2] - last_edit >= .290
    assert starts[0][1] == w._spec_for("bw-t180")
    assert starts[0][1]["t"] == 202 and starts[0][1]["dpi"] == 150
    assert starts[0][1]["force_raster"] and starts[0][1]["page_size"] == "letter"
    assert w._shown_preview_key == wanted
    assert w.after._pdf_source.path == w._artifacts.results[wanted].pdf_path


@pytest.mark.parametrize("control", ["indexed", "strategy", "lossless"])
def test_remaining_recipe_controls_share_the_same_timer_and_update(window, monkeypatch, control):
    w = window
    pid = {"indexed": "color-p16", "strategy": "bw-t180", "lossless": "color-j2k"}[control]
    choose(w, pid)
    starts, start = [], w._artifacts.start
    def count(*args, **kwargs):
        worker = start(*args, **kwargs)
        if worker is not None:
            starts.append(args[0])
        return worker
    monkeypatch.setattr(w._artifacts, "start", count)
    if control == "indexed":
        w.colors_value.stepDown()
        w.colors.setValue(8)
        w.colors_value.selectAll()
        QTest.keyClicks(w.colors_value, "4")
    elif control == "strategy":
        w.strategy.setCurrentText("otsu")
    else:
        w.lossless_box.setChecked(True)
    wanted = w._result_key(pid)
    assert w._preview_timer.isActive() and not starts
    QTest.qWait(220)
    assert w._preview_timer.isActive() and not starts
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert starts == [wanted] and w._shown_preview_key == wanted
    assert w._mini_amount[pid] == w._sized(w._artifacts.results[wanted].nbytes)
    if control == "indexed":
        assert w._spec_for(pid)["colors"] == w.colors_value.value() == w.colors.value() == 4


@pytest.mark.parametrize("choice", ("save", "discard", "save_as", "cancel"))
@pytest.mark.parametrize("entry", ("dropdown", "mini", "keyboard"))
def test_switch_decisions_keep_the_correct_files(window, monkeypatch, choice, entry):
    w = window
    saved_key = w._result_key("bw-t180")
    saved = w._artifacts.results[saved_key]
    live = edit(w)
    live_key = w._result_key("bw-t180")
    generation = w._gen
    previous_ids = set(w._strip_ids)
    prompts = []
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: prompts.append(pid) or choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Saved live copy", True))
    target_pid = w._strip_ids[w._strip_ids.index("bw-t180")+1]
    request_filter(w, target_pid, entry)
    assert prompts == ["bw-t180"]
    wait_until(lambda: not w._artifacts.pending)
    assert w._gen == generation and not w._artifacts.pending
    if choice == "cancel":
        assert w._active_pid == "bw-t180" and w.slider.value() == 203
        assert w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == "bw-t180"
        assert [item.data(Qt.UserRole) for item in w.filters.selectedItems()] == ["bw-t180"]
        assert "bw-t180" in w._draft_specs
        assert Path(saved.pdf_path).is_file() and Path(live.pdf_path).is_file()
    else:
        selected = next(iter(set(w._strip_ids)-previous_ids)) if choice == "save_as" else target_pid
        assert w._active_pid == selected and "bw-t180" not in w._draft_specs
        assert w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == selected
        assert [item.data(Qt.UserRole) for item in w.filters.selectedItems()] == [selected]
        if choice == "save":
            assert not Path(saved.pdf_path).exists() and Path(live.pdf_path).is_file()
            assert w._saved_specs["bw-t180"]["t"] == 203
            assert w._result_key("bw-t180") == live_key
        elif choice == "discard":
            assert Path(saved.pdf_path).is_file() and not Path(live.pdf_path).exists()
            assert w._saved_specs["bw-t180"]["t"] == 180
        else:
            nid, = set(w._strip_ids) - previous_ids
            copied = w._artifacts.results[w._result_key(nid)]
            assert Path(saved.pdf_path).is_file() and Path(copied.pdf_path).is_file()
            assert w._result_key(nid) != live_key
            assert copied.nbytes == live.nbytes
            assert presets.get(nid)["uuid"] != presets.get("bw-t180")["uuid"]
            assert w._saved_specs["bw-t180"]["t"] == 180
            assert w._saved_specs[nid]["t"] == 203
            assert w.slider.value() == 203 and not w.isWindowModified()
            assert w._shown_preview_key == w._result_key(nid)
            selected_rect = w.filters.visualItemRect(w.filters.currentItem())
            visible = selected_rect.intersected(w.filters.viewport().rect())
            # Qt's terminal IconMode grid can round the last edge by one pixel.
            assert visible.width() >= selected_rect.width()-1


@pytest.mark.parametrize("dismissal", ("escape", "cancel", "close"))
@pytest.mark.parametrize("gesture", ("mini", "keyboard", "after_reorder"))
def test_real_mini_click_cancel_keeps_current_and_selected_draft(window, dismissal, gesture):
    """§161: inspect selection after Qt finishes the full native mouse gesture."""
    w = window
    saved = w._artifacts.results[w._result_key("bw-t180")]
    live = edit(w)
    shown, generation = w._shown_preview_key, w._gen
    drafts = copy.deepcopy(w._draft_specs)
    artifacts = dict(w._artifacts.results)
    errors, prompts = [], []
    v = w.filters
    if gesture == "after_reorder":
        assert v.model().moveRow(QModelIndex(), w._strip_ids.index("bw-otsu"), QModelIndex(), 8)
    target = v.item(w._strip_ids.index("bw-otsu"))
    v.scrollToItem(target)
    _app.processEvents()

    def dismiss():
        box = _app.activeModalWidget()
        if box is None:
            return
        try:
            assert isinstance(box, QMessageBox), "mini click did not show the real decision dialog"
            prompts.append(box.windowTitle())
            assert w._active_pid == "bw-t180"
            if dismissal == "escape":
                QTest.keyClick(box, Qt.Key_Escape)
            elif dismissal == "cancel":
                QTest.mouseClick(box.button(QMessageBox.Cancel), Qt.LeftButton)
            else:
                box.close()
        except Exception as exc:
            errors.append(str(exc))
            if box is not None:
                box.reject()

    for _ in range(2):
        dismiss_timer = QTimer(w)
        dismiss_timer.setInterval(50)
        dismiss_timer.timeout.connect(dismiss)
        dismiss_timer.start()
        try:
            if gesture == "keyboard":
                QTest.keyClick(v, Qt.Key_Home)
            else:
                v.scrollToItem(target)
                _app.processEvents()
                QTest.mouseClick(v.viewport(), Qt.LeftButton, Qt.NoModifier, v.visualItemRect(target).center())
        finally:
            dismiss_timer.stop()
        _app.processEvents()
        assert not errors, errors
        assert w._active_pid == w.preset.currentData() == v.currentItem().data(Qt.UserRole) == "bw-t180"
        assert [item.data(Qt.UserRole) for item in v.selectedItems()] == ["bw-t180"], (
            dismissal, "Qt finished highlighting the attempted filter after cancellation")
        assert w._shown_preview_key == shown and w.slider.value() == 203
        assert w._draft_specs == drafts and w.isWindowModified()
        assert w._gen == generation and w._artifacts.results == artifacts
        assert Path(saved.pdf_path).is_file() and Path(live.pdf_path).is_file()
    assert prompts == ["Unsaved filter changes"] * 2


@pytest.mark.parametrize("entry", ("dropdown", "mini", "keyboard"))
@pytest.mark.parametrize("name_result", (("", False), ("   ", True)))
def test_canceling_save_as_naming_cancels_switch(window, monkeypatch, entry, name_result):
    w = window
    live = edit(w)
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "save_as")
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: name_result)
    request_filter(w, w._strip_ids[w._strip_ids.index("bw-t180")+1], entry)
    assert w._active_pid == "bw-t180" and w.slider.value() == 203
    assert w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == "bw-t180"
    assert "bw-t180" in w._draft_specs and Path(live.pdf_path).is_file()


def test_explicit_save_keeps_live_artifact_without_reprocessing(window):
    w = window
    live = edit(w)
    generation = w._gen
    w.save_filter()
    assert not w._draft_specs and not w.isWindowModified()
    assert w._gen == generation
    assert w._artifacts.results[w._result_key("bw-t180")] is live
    assert presets.get("bw-t180")["params"]["t"] == 203


@pytest.mark.parametrize("state", ("ready", "debounced", "pending"))
def test_revert_button_reuses_saved_file_and_keeps_selection(window, monkeypatch, state):
    """§162: revert uses Discard ownership, including before/during processing."""
    w = window
    choose(w, "bw-t180")
    saved_key = w._result_key("bw-t180")
    saved = w._artifacts.results[saved_key]
    other_results = {key: value for key, value in w._artifacts.results.items() if key != saved_key}
    assert not w.revert_btn.isEnabled() and not w.revert_btn.icon().isNull()
    assert w.revert_btn.text() == "" and w.revert_btn.toolTip() == "Revert Changes"
    w.slider.setValue(203)
    draft_key = w._result_key("bw-t180")
    if state == "ready":
        wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
        draft_path = Path(w._artifacts.results[draft_key].pdf_path)
    elif state == "pending":
        w._preview_timer.stop()
        w._dispatch_filters()
        assert draft_key in w._artifacts.pending
    assert w.revert_btn.isEnabled() and w.preset.currentText().endswith(" *")
    generation = w._gen

    def forbidden(*args, **kwargs):
        pytest.fail("Revert must reuse the existing saved file, not submit filtering")

    monkeypatch.setattr(w._artifacts, "start", forbidden)
    QTest.mouseClick(w.revert_btn, Qt.LeftButton)
    wait_until(lambda: not w._artifacts.pending and not w._jobs)
    assert w._active_pid == w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == "bw-t180"
    assert [item.data(Qt.UserRole) for item in w.filters.selectedItems()] == ["bw-t180"]
    assert not w._draft_specs and not w.isWindowModified()
    assert w.slider.value() == 180 and not w._preview_timer.isActive()
    assert not w.revert_btn.isEnabled() and not w.keep_btn.isEnabled()
    assert w._gen == generation and w._shown_preview_key == saved_key
    assert w._artifacts.results[saved_key] is saved and Path(saved.pdf_path).is_file()
    assert draft_key not in w._artifacts.results and draft_key not in w._artifacts.pending
    assert all(w._artifacts.results[key] is value for key, value in other_results.items())
    if state == "ready":
        assert not draft_path.exists()


def test_copied_saved_artifact_is_independent_and_not_refiltered(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    original = w._artifacts.results[w._result_key("bw-t180")]
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Kept copy", True))
    generation = w._gen
    w.copy_filter()
    wait_until(lambda: not w._artifacts.pending)
    copied = w._active_pid
    duplicate = w._artifacts.results[w._result_key(copied)]
    assert duplicate.pdf_path != original.pdf_path
    assert Path(duplicate.pdf_path).read_bytes() == Path(original.pdf_path).read_bytes()
    assert Path(duplicate.directory).parent.name == presets.get(copied)["uuid"]
    assert w._gen == generation
    edit(w)
    w.save_filter()
    assert Path(duplicate.pdf_path).is_file()
    assert w._artifacts.results[w._result_key(copied)] is duplicate


class ControlledExecutor:
    def __init__(self):
        self.requests = []

    def submit(self, function, *args):
        future = Future()
        self.requests.append((future, function, args))
        return future


@pytest.mark.parametrize("entry", ("dropdown", "mini", "keyboard", "explicit"))
def test_save_as_before_debounce_selects_copy_and_submits_recipe_once(window, monkeypatch, entry):
    w = window
    choose(w, "bw-t180")
    saved = w._artifacts.results[w._result_key("bw-t180")]
    before = set(w._strip_ids)
    executor = ControlledExecutor()
    monkeypatch.setattr(ui, "filter_pool", lambda: executor)
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "save_as")
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Before debounce", True))
    w.slider.setValue(203)
    assert w._preview_timer.isActive() and not executor.requests
    if entry == "explicit":
        w.copy_filter()
    else:
        request_filter(w, w._strip_ids[w._strip_ids.index("bw-t180")+1], entry)
    nid, = set(w._strip_ids)-before
    assert w._active_pid == w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == nid
    assert w.slider.value() == 203 and not w._draft_specs and not w._preview_timer.isActive()
    assert len(executor.requests) == 1
    future, function, args = executor.requests[0]
    assert args[1]["t"] == 203
    future.set_result(function(*args))
    wait_until(lambda: not w._artifacts.pending)
    assert len(executor.requests) == 1 and w._shown_preview_key == w._result_key(nid)
    assert w._saved_specs["bw-t180"]["t"] == 180 and Path(saved.pdf_path).is_file()
    assert w._saved_specs[nid]["t"] == 203


@pytest.mark.parametrize("action", ("open", "close", "cancel_both"))
def test_save_as_open_close_preserves_requested_action(window, monkeypatch, tmp_path, action):
    w = window
    live = edit(w)
    before = set(w._strip_ids)
    old_path = w.path
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "save_as")
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k:
                        ("", False) if action == "cancel_both" else ("Open close copy", True))
    replacement = tmp_path / "next.pdf"
    with fitz.open() as doc:
        doc.new_page().insert_text((20, 80), "Another input")
        doc.save(replacement)
    if action in ("open", "cancel_both"):
        w.open_file(str(replacement))
    if action in ("close", "cancel_both"):
        w.close()
    if action == "cancel_both":
        assert set(w._strip_ids) == before and w.path == old_path
        assert w._active_pid == "bw-t180" and not w._closing_requested
        assert "bw-t180" in w._draft_specs and Path(live.pdf_path).is_file()
    else:
        nid, = set(w._strip_ids)-before
        assert w._active_pid == w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == nid
        assert w._saved_specs[nid]["t"] == 203 and w._saved_specs["bw-t180"]["t"] == 180
        if action == "open":
            wait_until(lambda: not w._artifacts.pending)
            assert w.path == str(replacement) and w._shown_preview_key == w._result_key(nid)
        else:
            wait_until(lambda: not w._jobs)
            assert w._closing_requested
            assert any(p["id"] == nid for p in w._custom_store().value("customPresets"))


def test_submission_priority_is_selected_first_then_strip_order(window, monkeypatch):
    executor = ControlledExecutor()
    monkeypatch.setattr(ui, "filter_pool", lambda: executor)
    w = ui.MainWindow()
    choose(w, "bw-t210")
    try:
        w.open_file(window.path)
        assert [spec_key(args[1]) for _, _, args in executor.requests] == [
            spec_key(w._spec_for(pid)) for pid in w._ordered_pids()]
        assert len(executor.requests) == len(w._strip_ids)
    finally:
        w.close()
        wait_until(lambda: not w._jobs)


def test_uuid_and_paths_survive_rename_reorder_and_recipe_save(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    uid = presets.get("bw-t180")["uuid"]
    original = w._artifacts.results[w._result_key("bw-t180")]
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("New display name", True))
    w.rename_filter()
    assert w.filters._move_to_gap(4)
    assert presets.get("bw-t180")["uuid"] == uid
    assert w._artifacts.results[w._result_key("bw-t180")] is original
    assert uid not in w.preset.currentText()
    live = edit(w)
    w.save_filter()
    assert presets.get("bw-t180")["uuid"] == uid
    assert Path(live.directory).parent.name == uid
    persisted = next(p for p in w._custom_store().value("customPresets") if p["id"] == "bw-t180")
    assert persisted["uuid"] == uid


@pytest.mark.parametrize("choice", ("save", "discard", "save_as"))
def test_switch_while_live_processing_is_pending(window, monkeypatch, choice):
    w = window
    choose(w, "bw-t180")
    saved = w._artifacts.results[w._result_key("bw-t180")]
    executor = ControlledExecutor()
    monkeypatch.setattr(ui, "filter_pool", lambda: executor)
    w.slider.setValue(203)
    wait_until(lambda: bool(executor.requests))
    live_key = w._result_key("bw-t180")
    assert live_key in w._artifacts.pending
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Pending copy", True))
    before_ids = set(w._strip_ids)
    w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
    current_preview = w._shown_preview_key
    assert len(executor.requests) == 1  # promotion must not submit it twice
    future, function, args = executor.requests[0]
    result = function(*args)
    future.set_result(result)
    if choice == "save_as":
        wait_until(lambda: len(executor.requests) == 2)
        copy_future, copy_function, copy_args = executor.requests[1]
        assert copy_function.__name__ == "copy_artifact"  # no second real saver
        copy_future.set_result(copy_function(*copy_args))
    wait_until(lambda: not w._artifacts.pending)
    if choice != "save_as":
        assert w._shown_preview_key == current_preview  # unrelated arrivals cannot steal preview
    if choice == "discard":
        assert Path(saved.pdf_path).is_file() and not Path(result.pdf_path).exists()
        assert live_key not in w._artifacts.results
    else:
        if choice == "save":
            assert Path(result.pdf_path).is_file() and live_key in w._artifacts.results
            assert not Path(saved.pdf_path).exists()
        else:
            nid, = set(w._strip_ids) - before_ids
            copied = w._artifacts.results[w._result_key(nid)]
            assert w._active_pid == w.preset.currentData() == w.filters.currentItem().data(Qt.UserRole) == nid
            assert w._shown_preview_key == w._result_key(nid)  # the active pending copy must publish
            assert w._result_key(nid) != live_key and Path(saved.pdf_path).is_file()
            assert Path(copied.pdf_path).is_file() and copied.nbytes == result.nbytes


def test_pdf_export_is_the_exact_displayed_file(window, monkeypatch, tmp_path):
    w = window
    choose(w, "color-p16")
    result = w._artifacts.results[w._result_key(w._active_pid)]
    generation = w._gen
    out = tmp_path / "export.pdf"
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: (str(out), "PDF"))
    w.save()
    wait_until(lambda: not w._jobs)
    assert out.read_bytes() == Path(result.pdf_path).read_bytes()
    assert out.stat().st_size == result.nbytes
    assert w._gen == generation and not w._export_keys


def test_dirty_open_and_close_cancel_preserve_state(window, monkeypatch, tmp_path):
    w = window
    live = edit(w)
    original_path, original_preview = w.path, w._shown_preview_key
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: "cancel")
    replacement = tmp_path / "replacement.pdf"
    with fitz.open() as doc:
        doc.new_page()
        doc.save(replacement)
    w.open_file(str(replacement))
    assert w.path == original_path and w._shown_preview_key == original_preview
    w.close()
    assert not w._closing_requested and w.doc is not None
    assert "bw-t180" in w._draft_specs and Path(live.pdf_path).is_file()


def test_prompt_uses_standard_save_discard_cancel_and_save_as(window):
    box, save_as = window._make_unsaved_dialog("bw-t180")
    assert box.standardButtons() == (QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    assert box.button(QMessageBox.Discard).text() == "Discard Changes"
    assert box.buttonRole(box.button(QMessageBox.Discard)) == QMessageBox.DestructiveRole
    assert box.escapeButton() == box.button(QMessageBox.Cancel)
    assert save_as.text() == "Save As…"
    box.close()


def test_one_saver_call_then_only_file_observation(tmp_path, monkeypatch):
    source, root = tmp_path / "source.pdf", tmp_path / "artifact"
    root.mkdir()
    with fitz.open() as doc:
        doc.new_page().insert_text((20, 80), "One actual saver call")
        doc.save(source)
    calls, saver = [], pipeline.save_with_spec

    def record(*args, **kwargs):
        calls.append(dict(args[2]))
        return saver(*args, **kwargs)

    monkeypatch.setattr(pipeline, "save_with_spec", record)
    result = build_artifact(str(source), preset_spec(presets.get("bw-t180")), str(root))
    assert len(calls) == 1
    _ = result.pages, result.mini_pages, result.nbytes
    assert len(calls) == 1 and result.nbytes == Path(result.pdf_path).stat().st_size
    result.close_pages()


def test_effective_recipe_keys_include_all_saver_inputs_not_names():
    bw = preset_spec(presets.get("bw-t180"))
    assert spec_key(bw) == spec_key(dict(bw, preset_id="another-name"))
    for field, value in (("dpi", 600), ("t", 203), ("strategy", "sauvola"),
                         ("force_raster", True)):
        assert spec_key(bw) != spec_key(dict(bw, **{field: value}))
    automatic = dict(bw, strategy="otsu")
    assert spec_key(automatic) == spec_key(dict(automatic, t=255))
    assert spec_key(bw) == spec_key(dict(bw, page_size="a4"))  # unforced ignores size
    forced = dict(bw, force_raster=True)
    assert spec_key(forced) != spec_key(dict(forced, page_size="a4"))
    for mode, field in (("color", "jpeg_q"), ("jpx", "jpx_q"), ("indexed", "colors")):
        sample = next(p for p in presets.PRESETS if p["mode"] == mode)
        spec = preset_spec(sample)
        assert spec_key(spec) != spec_key(dict(spec, **{field: spec[field] + 1}))


def test_temp_sweeper_protects_live_processes_and_fresh_empty_folders(tmp_path):
    saves = tmp_path / "pdf-minify" / "saves"
    saves.mkdir(parents=True)
    live = ArtifactStore(str(saves))
    root = Path(live.root)
    assert root.name == str(os.getpid())
    empty_worker = root / "filter-pending"
    empty_worker.mkdir()
    old_file = root / "old-but-owned.pdf"
    old_file.write_bytes(b"owned by this running GUI")
    expired = time.time() - 72 * 3600
    os.utime(root, (expired, expired))
    os.utime(empty_worker, (expired, expired))
    os.utime(old_file, (expired, expired))
    fresh = saves / "999997" / "filter-fresh"
    fresh.mkdir(parents=True)
    dead = saves / "999998" / "filter-old"
    dead.mkdir(parents=True)
    stale = dead / "filtered.pdf"
    stale.write_bytes(b"disposable expired output")
    for path in (stale, dead, dead.parent):
        os.utime(path, (expired, expired))
    try:
        assert sweep_stale_temps(temp_base=str(tmp_path)) == 1
        assert old_file.read_bytes() == b"owned by this running GUI"
        assert empty_worker.is_dir() and fresh.is_dir()
        assert not stale.exists() and not dead.exists()
    finally:
        old_file.unlink()
        empty_worker.rmdir()
        live.close()


def test_pid_directory_is_exclusive_and_removed_on_normal_exit(tmp_path):
    from pdf_minify.ui_qt.artifacts import FilterArtifact
    saves = tmp_path / "pdf-minify" / "saves"
    store = ArtifactStore(str(saves))
    root = Path(store.root)
    assert root == saves / str(os.getpid())
    try:
        with pytest.raises(RuntimeError, match="already owned"):
            ArtifactStore(str(saves))
        key = store.key("input", preset_spec(presets.get("bw-t180")),
                        presets.get("bw-t180")["uuid"])
        directory = Path(store._allocate(key))
        output = directory / "filtered.pdf"
        output.write_bytes(b"owned disposable bytes")
        store.results[key] = FilterArtifact(str(directory), str(output), output.stat().st_size, [])
    finally:
        store.close()
    assert not root.exists()  # no session/history retained


def test_retired_copy_keeps_source_until_copy_worker_finishes(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    source = w._artifacts.results[w._result_key("bw-t180")]
    executor = ControlledExecutor()
    monkeypatch.setattr(ui, "filter_pool", lambda: executor)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("In-flight copy", True))
    w.copy_filter()
    target = w._result_key(w._active_pid)
    assert len(executor.requests) == 1
    store = w._artifacts
    store.retain(set())  # simulate releasing all view refs during a file change
    assert target in store.retired and Path(source.pdf_path).exists()
    future, function, args = executor.requests[0]
    result = function(*args)
    future.set_result(result)
    wait_until(lambda: target not in store.pending)
    assert not Path(result.pdf_path).exists()


@pytest.mark.parametrize("mode", ("color", "jpx", "indexed", "bw"))
def test_real_image_payloads_decode_without_hidden_compression(tmp_path, mode):
    """B79: exercise real image streams, not just text-only PDFs/helper arrays."""
    import io
    from PIL import Image
    rng = np.random.default_rng(123)
    pixels = rng.integers(0, 256, (320, 320, 3), dtype=np.uint8)
    # Flat bands plus noise make every chosen codec's actual insertion path run.
    pixels[:80] = (220, 30, 60)
    pixels[80:160] = (30, 220, 60)
    buf = io.BytesIO()
    Image.fromarray(pixels).save(buf, "PNG")
    source, root = tmp_path / "images.pdf", tmp_path / "result"
    root.mkdir()
    with fitz.open() as doc:
        page = doc.new_page(width=180, height=180)
        page.insert_image(fitz.Rect(10, 10, 170, 170), stream=buf.getvalue())
        doc.save(source)
    preset = next(p for p in presets.PRESETS if p["mode"] == mode)
    spec = preset_spec(preset)
    if mode == "bw":
        spec["force_raster"] = False
    result = build_artifact(str(source), spec, str(root))
    with fitz.open(result.pdf_path) as doc:
        image = fitz.Pixmap(doc, doc[0].get_images()[0][0])
        assert image.width > 0 and image.height > 0
        assert np.frombuffer(image.samples, dtype=np.uint8).std() > 10
    assert np.asarray(result.pages[0]).std() > 10
    assert not fitz.TOOLS.mupdf_warnings()
    result.close_pages()


def test_corrupt_saved_image_is_rejected_not_shown_as_valid(tmp_path, monkeypatch):
    import io
    from PIL import Image
    root = tmp_path / "result"
    root.mkdir()
    source = tmp_path / "input.pdf"
    with fitz.open() as doc:
        doc.new_page()
        doc.save(source)

    def corrupt_saver(input_path, output_path, spec, token, progress, **kwargs):
        with fitz.open() as doc:
            page = doc.new_page(width=100, height=100)
            buf = io.BytesIO()
            Image.new("RGB", (200, 200), "red").save(buf, "PNG")
            xref = page.insert_image(page.rect, stream=buf.getvalue())
            doc.update_stream(xref, b"not a JPEG", compress=False)
            doc.xref_set_key(xref, "Filter", "/DCTDecode")
            doc.save(output_path)

    monkeypatch.setattr(pipeline, "save_with_spec", corrupt_saver)
    with pytest.raises(ValueError, match="readback failed"):
        build_artifact(str(source), {"mode": "color"}, str(root))


def test_zopfli_uses_valid_zlib_container_and_rejects_bad_output(tmp_path, monkeypatch):
    import gzip
    import zlib
    from types import SimpleNamespace
    payload = b"PDF Flate stream " * 300
    commands = []
    monkeypatch.setattr(pipeline, "zopfli_binary", lambda: "/usr/bin/zopfli")

    def wrong_container(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout=gzip.compress(payload))

    monkeypatch.setattr(pipeline.subprocess, "run", wrong_container)
    token = pipeline._ENCODE_WORKDIR.set(str(tmp_path))
    try:
        result = pipeline.deflate_best(payload)
    finally:
        pipeline._ENCODE_WORKDIR.reset(token)
    assert "--zlib" in commands[0]
    assert Path(commands[0][-1]).parent == tmp_path
    assert zlib.decompress(result) == payload
    assert not list(tmp_path.iterdir())  # no escaped/leaked encoder scratch


def test_every_filter_can_edit_all_six_image_algorithms_without_changing_identity(window):
    from pdf_minify.core.algorithms import ALGORITHMS, BW_MODES, PALETTE_MODES
    w = window
    choose(w, "bw-t180")
    pid = w._active_pid
    saved, uid, name = dict(w._saved_specs[pid]), presets.get(pid)["uuid"], w._preset_label(pid)
    saved_result = w._artifacts.results[w._result_key(pid)]
    order = w._strip_ids
    assert w.strategy_label.text().replace("&", "") == "Threshold method:"
    for mode, label in ALGORITHMS:
        w.compression.setCurrentIndex(w.compression.findData(mode))
        spec = w._spec_for(pid)
        assert spec["mode"] == mode and w._saved_specs[pid] == saved
        assert w._active_pid == pid and presets.get(pid)["uuid"] == uid
        assert w._preset_label(pid) == name and w._strip_ids == order
        assert w.dpi.currentData() == 300
        assert w.strategy.isEnabled() == (mode in BW_MODES)
        assert w.threshold_control.isEnabled() == (mode in BW_MODES)
        assert w.colors_control.isEnabled() == (mode in PALETTE_MODES)
        assert w.force_raster.isEnabled()
        assert w.lossless_box.isEnabled() == (mode == "jpx")
        assert w.details.text().splitlines()[0] == "Codec: "+label
        if mode == "jpx":
            assert not w.lossless_box.isChecked()  # not the old BW fixed state
        if mode == "layered-jbig2":
            assert w.colors_value.value() == 5
    w.revert_filter()
    assert w.compression.currentData() == "bw" and not w._draft_specs
    assert os.path.isfile(saved_result.pdf_path)
    assert "Threshold method: simple" in w.details.text() and "T=180" in w.details.text()
    w.strategy.setCurrentText("otsu")
    assert "Threshold method: otsu (automatic)" in w.details.text()
    assert "T=" not in w.details.text() and not w.threshold_control.isEnabled()
    w.revert_filter()


def test_image_and_native_compression_share_single_trailing_edit_debounce(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    calls = []
    start = w._artifacts.start
    def record(key, path, spec, *args, **kwargs):
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None:
            calls.append(dict(spec))
        return worker
    monkeypatch.setattr(w._artifacts, "start", record)
    w.compression.setCurrentIndex(w.compression.findData("indexed"))
    QTest.qWait(40)
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    QTest.qWait(40)
    w.compression.setCurrentIndex(w.compression.findData("layered-jbig2"))
    QTest.qWait(40)
    w.colors_value.setValue(4)
    assert not calls and w._preview_timer.isActive()
    assert w._filter_display_name(w._active_pid).endswith(" *")
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(calls) == 1 and calls[0]["mode"] == "layered-jbig2"
    assert calls[0]["stream_compression"] == "zopfli" and calls[0]["colors"] == 4
    result = w._artifacts.results[w._result_key(w._active_pid)]
    assert result.nbytes == os.path.getsize(result.pdf_path)
    assert w.after._pdf_source.path == result.pdf_path


def test_full_page_flag_remains_effective_when_changing_between_bw_and_color(window):
    w = window
    choose(w, "bw-fast")
    assert w.force_raster.isChecked() and w.force_raster.isEnabled()
    original = dict(w._saved_specs["bw-fast"])
    w.compression.setCurrentIndex(w.compression.findData("color"))
    assert w.force_raster.isEnabled() and w.force_raster.isChecked()
    assert "Full-page raster" in w.details.text()
    assert w._spec_for("bw-fast")["force_raster"]
    assert spec_key(w._spec_for("bw-fast")) != spec_key(dict(w._spec_for("bw-fast"), force_raster=False))
    w.compression.setCurrentIndex(w.compression.findData("bw"))
    assert w.force_raster.isChecked() and w.force_raster.isEnabled()
    assert spec_key(w._spec_for("bw-fast")) == spec_key(original)
    assert not w._draft_specs


@pytest.mark.parametrize("mode", ["color", "jpx", "indexed", "layered-jbig2"])
def test_color_ffpr_uses_one_debounced_real_file_and_revert_reuses_saved_result(window, monkeypatch, mode):
    w = window
    choose(w, "color-p16")
    pid = w._active_pid
    saved_key = w._result_key(pid)
    saved = w._artifacts.results[saved_key]
    starts = []
    start = w._artifacts.start
    def record(key, path, spec, *args, **kwargs):
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None:
            starts.append(dict(spec))
        return worker
    monkeypatch.setattr(w._artifacts, "start", record)
    w.compression.setCurrentIndex(w.compression.findData(mode))
    w.force_raster.setChecked(True)
    assert w.force_raster.isEnabled() and w.page_size.isEnabled()
    assert not starts and w._preview_timer.isActive()
    assert w._filter_display_name(pid).endswith(" *")
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1 and starts[0]["force_raster"] and starts[0]["dpi_cap"] == 300
    result = w._artifacts.results[w._result_key(pid)]
    assert result.nbytes == os.path.getsize(result.pdf_path)
    assert w.after._pdf_source.path == result.pdf_path
    assert "Full-page raster" in w.details.text() and "FFPR" in ui._preset_algo(pid, w._spec_for(pid))
    with fitz.open(result.pdf_path) as doc:
        assert all(not page.get_text("words") for page in doc)
    w.revert_filter()
    assert w._result_key(pid) == saved_key and w._artifacts.results[saved_key] is saved
    assert not w.force_raster.isChecked() and len(starts) == 1


@pytest.mark.parametrize("policy", ["brotli", "best"])
def test_changed_algorithm_and_native_compression_save_and_reload_builtin_override(window, policy):
    w = window
    choose(w, "bw-t180")
    uid = presets.get("bw-t180")["uuid"]
    w.compression.setCurrentIndex(w.compression.findData("layered-jbig2"))
    w.stream_compression.setCurrentIndex(w.stream_compression.findData(policy))
    assert w.stream_compression.toolTip() == ui.STREAM_HELP[policy]
    assert not w.brotli_declaration.isChecked() and not w.brotli_declaration.isHidden()
    w.brotli_declaration.setChecked(True)
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    result = w._artifacts.results[w._result_key("bw-t180")]
    w.save_filter()
    assert not w._draft_specs and presets.get("bw-t180")["mode"] == "layered-jbig2"
    persisted = next(p for p in w._custom_store().value("customPresets") if p["id"] == "bw-t180")
    assert persisted["mode"] == "layered-jbig2" and persisted["uuid"] == uid
    assert persisted["params"]["stream_compression"] == policy
    assert persisted["params"]["brotli_declaration"] is True
    assert w._artifacts.results[w._result_key("bw-t180")] is result
    # A fresh process starts from built-in templates, NOT the modified globals.
    presets.PRESETS[:] = copy.deepcopy(_defaults)
    loaded = ui.MainWindow(None)
    try:
        choose(loaded, "bw-t180")
        assert loaded.compression.currentData() == "layered-jbig2"
        assert loaded.stream_compression.currentData() == policy
        assert loaded.brotli_declaration.isChecked() and not loaded.brotli_declaration.isHidden()
        assert loaded.colors_value.value() == 5 and loaded.colors_control.isEnabled()
        assert not loaded.strategy.isEnabled() and not loaded._draft_specs
        assert presets.get("bw-t180")["uuid"] == uid
    finally:
        loaded.close()


def test_brotli_compatibility_is_hidden_elsewhere_and_shares_the_real_edit_debounce(window, monkeypatch):
    from pdf_minify.core.stream_compression import brotli_declaration_present

    w = window
    choose(w, "bw-t180")
    # The app now defaults to Best (also Brotli-capable). Establish an explicit
    # ordinary-Flate baseline for this fixed-policy visibility/debounce test.
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("flate"))
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    w.save_filter()
    assert w.brotli_declaration.isHidden() and not w.brotli_declaration.isChecked()
    assert w.brotli_declaration.text() == "Include Brotli extension declaration (Compatibility)"
    calls = []
    start = w._artifacts.start
    def record(key, path, spec, *args, **kwargs):
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None:
            calls.append(dict(spec))
        return worker
    monkeypatch.setattr(w._artifacts, "start", record)
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("brotli"))
    assert w.brotli_declaration.isVisible() and w.brotli_declaration.isEnabled()
    assert not w.brotli_declaration.isChecked()
    QTest.qWait(40)
    w.brotli_declaration.setChecked(True)
    QTest.qWait(40)
    w.brotli_declaration.setChecked(False)
    QTest.qWait(40)
    w.brotli_declaration.setChecked(True)
    assert not calls and w._preview_timer.isActive()
    assert w._filter_display_name(w._active_pid).endswith(" *")
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(calls) == 1 and calls[0]["brotli_declaration"] is True
    enabled = w._artifacts.results[w._result_key(w._active_pid)]
    with fitz.open(enabled.pdf_path) as doc:
        assert brotli_declaration_present(doc)
    w.save_filter()  # protect this completed saved artifact while editing its draft
    w.brotli_declaration.setChecked(False)
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    default = w._artifacts.results[w._result_key(w._active_pid)]
    with fitz.open(default.pdf_path) as doc:
        assert not brotli_declaration_present(doc)
    assert default.nbytes < enabled.nbytes
    assert w.after._pdf_source.path == default.pdf_path
    w.brotli_declaration.setChecked(True)  # exact completed artifact is reusable
    assert w._artifacts.results[w._result_key(w._active_pid)] is enabled
    assert len(calls) == 2
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    assert w.brotli_declaration.isHidden() and w.brotli_declaration.isChecked()
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("brotli"))
    assert w.brotli_declaration.isVisible() and w.brotli_declaration.isChecked()
    choose(w, "color-max")  # clean switch to another default-OFF filter
    assert w.stream_compression.currentData() == "best"
    assert w.brotli_declaration.isVisible() and not w.brotli_declaration.isChecked()
    assert not w._draft_specs


def test_brotli_warning_is_native_contextual_help_without_inline_space_or_processing(window):
    w = window
    choose(w, "bw-t180")
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("brotli"))
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    combo = w.stream_compression
    assert not hasattr(w, "stream_warning")
    assert combo.toolTip() == combo.accessibleDescription() == ui.STREAM_HELP["brotli"]
    assert combo.whatsThis().startswith(combo.toolTip())
    for policy, _ in ui.STREAM_POLICIES:
        assert combo.itemData(combo.findData(policy), Qt.ToolTipRole) == ui.STREAM_HELP[policy]
    snapshot = (w._gen, dict(w._artifacts.results), dict(w._draft_specs), w._active_pid)
    local = combo.rect().center()
    _app.sendEvent(combo, QHelpEvent(QEvent.ToolTip, local, combo.mapToGlobal(local)))
    _app.processEvents()
    assert QToolTip.isVisible() and QToolTip.text() == ui.STREAM_HELP["brotli"]
    QToolTip.hideText()
    assert snapshot == (w._gen, dict(w._artifacts.results), dict(w._draft_specs), w._active_pid)
    assert not w._preview_timer.isActive() and not w._artifacts.pending
    w.revert_filter()
    assert combo.toolTip() == combo.accessibleDescription() == ui.STREAM_HELP["best"]


@pytest.mark.parametrize("choice", ["cancel", "discard", "save_as"])
@pytest.mark.parametrize("policy", ["brotli", "best"])
def test_brotli_declaration_uses_existing_unsaved_switch_transaction(window, monkeypatch, choice, policy):
    w = window
    choose(w, "bw-t180")
    w.stream_compression.setCurrentIndex(w.stream_compression.findData(policy))
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    w.save_filter()
    saved_key = w._result_key("bw-t180")
    w.brotli_declaration.setChecked(True)
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    draft = w._artifacts.results[w._result_key("bw-t180")]
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Brotli compatibility copy", True))
    w.preset.setCurrentIndex(w.preset.findData("color-max"))
    assert w._saved_specs["bw-t180"]["brotli_declaration"] is False
    if choice == "cancel":
        assert w._active_pid == "bw-t180" and w.brotli_declaration.isChecked()
        assert Path(draft.pdf_path).is_file() and w._draft_specs
        w.revert_filter()
        assert w._result_key("bw-t180") == saved_key and not w.brotli_declaration.isChecked()
    elif choice == "discard":
        assert w._active_pid == "color-max" and w.stream_compression.currentData() == "best"
        assert not w.brotli_declaration.isHidden()
        assert not w._draft_specs
    else:
        assert w._active_pid not in ("bw-t180", "color-max")
        assert not w._draft_specs and w.brotli_declaration.isChecked()
        assert presets.get(w._active_pid)["params"]["brotli_declaration"] is True
        assert presets.get(w._active_pid)["params"]["stream_compression"] == policy
        wait_until(lambda: not w._artifacts.pending and w._result_key(w._active_pid) in w._artifacts.results)
        copied = w._artifacts.results[w._result_key(w._active_pid)]
        assert copied.nbytes == draft.nbytes and copied.pdf_path != draft.pdf_path


def test_best_and_packed_image_edits_share_one_debounce_and_real_file_reuse(window, monkeypatch):
    from pdf_minify.core.stream_compression import brotli_declaration_present

    w = window
    choose(w, "bw-t180")
    starts = []
    start = w._artifacts.start

    def record(key, path, spec, *args, **kwargs):
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None:
            starts.append(dict(spec))
        return worker

    monkeypatch.setattr(w._artifacts, "start", record)
    w.compression.setCurrentIndex(w.compression.findData("indexed"))
    w.dpi.setCurrentIndex(w.dpi.findData(150))
    w.force_raster.setChecked(True)
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("best"))
    assert w.stream_compression.currentText() == "Best (Zopfli/Brotli)"
    assert w.png_prediction.currentData() == "best" and not w.png_prediction.isEnabled()
    assert w.brotli_declaration.isVisible() and not w.brotli_declaration.isChecked()
    QTest.qWait(40)
    w.brotli_declaration.setChecked(True)
    QTest.qWait(40)
    w.colors_value.setValue(5)
    assert not starts and w._preview_timer.isActive()
    assert w._filter_display_name(w._active_pid).endswith(" *")
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1 and starts[0]["stream_compression"] == "best"
    result = w._artifacts.results[w._result_key(w._active_pid)]
    with fitz.open(result.pdf_path) as doc:
        images = [x for x in range(1, doc.xref_length()) if doc.xref_is_stream(x)
                  and doc.xref_get_key(x, "Subtype")[1] == "/Image"]
        assert images
        assert all(doc.xref_get_key(x, "Filter")[1] in ("/FlateDecode", "/BrotliDecode") for x in images)
        has_brotli = any(doc.xref_is_stream(x) and "/BrotliDecode" in doc.xref_get_key(x, "Filter")[1]
                         for x in range(1, doc.xref_length()))
        assert brotli_declaration_present(doc) is has_brotli
    assert result.nbytes == Path(result.pdf_path).stat().st_size
    assert w.after._pdf_source.path == result.pdf_path
    w.save_filter()
    choose(w, "color-max")
    choose(w, "bw-t180")
    assert w._artifacts.results[w._result_key("bw-t180")] is result
    assert len(starts) == 1 and not w._draft_specs
    assert w.stream_compression.currentData() == "best"


def test_prediction_control_retains_explicit_choice_across_best_and_jstar(window):
    w = window
    choose(w, "bw-t180")
    assert not w.png_prediction.isHidden() and not w.png_prediction.isEnabled()
    w.compression.setCurrentIndex(w.compression.findData("indexed"))
    assert w.png_prediction.currentData() == "best" and not w.png_prediction.isEnabled()
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    assert w.png_prediction.isEnabled() and w.png_prediction.currentData() == "off"
    w.png_prediction.setCurrentIndex(w.png_prediction.findData("on"))
    assert w._spec_for(w._active_pid)["png_prediction"] == "on"
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("best"))
    assert not w.png_prediction.isEnabled() and w.png_prediction.currentData() == "best"
    assert w._spec_for(w._active_pid)["png_prediction"] == "on"
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    assert w.png_prediction.isEnabled() and w.png_prediction.currentData() == "on"
    w.compression.setCurrentIndex(w.compression.findData("color"))
    assert not w.png_prediction.isEnabled() and w.png_prediction.currentData() == "off"
    assert w._spec_for(w._active_pid)["png_prediction"] == "on"
    w.compression.setCurrentIndex(w.compression.findData("indexed"))
    assert w.png_prediction.isEnabled() and w.png_prediction.currentData() == "on"
    assert w.png_prediction.accessibleName() == "PNG prediction"
    assert w.png_prediction.accessibleDescription() == w.png_prediction.toolTip()
    assert "No source PNG" in w.png_prediction.whatsThis()


def test_prediction_edits_debounce_once_save_copy_reload_and_revert_without_reprocessing(window, monkeypatch):
    w = window
    choose(w, "bw-t180")
    starts = []
    start = w._artifacts.start

    def record(key, path, spec, *args, **kwargs):
        copying = key in w._artifacts.copy_sources
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None and not copying:
            starts.append(dict(spec))
        return worker

    monkeypatch.setattr(w._artifacts, "start", record)
    w.compression.setCurrentIndex(w.compression.findData("indexed"))
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    w.dpi.setCurrentIndex(w.dpi.findData(150))
    w.force_raster.setChecked(True)
    w.colors_value.setValue(5)
    w.png_prediction.setCurrentIndex(w.png_prediction.findData("on"))
    QTest.qWait(40)
    w.png_prediction.setCurrentIndex(w.png_prediction.findData("best"))
    assert not starts and w._preview_timer.isActive() and w._draft_specs
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1 and starts[0]["png_prediction"] == "best"
    pid = w._active_pid
    result = w._artifacts.results[w._result_key(pid)]
    assert result.nbytes == Path(result.pdf_path).stat().st_size
    assert w.after._pdf_source.path == result.pdf_path
    w.save_filter()
    assert presets.get(pid)["params"]["png_prediction"] == "best"
    w.png_prediction.setCurrentIndex(w.png_prediction.findData("off"))
    assert w._draft_specs and w._preview_timer.isActive()
    w.revert_filter()
    assert not w._draft_specs and not w._preview_timer.isActive()
    assert w.png_prediction.currentData() == "best" and len(starts) == 1
    assert w._artifacts.results[w._result_key(pid)] is result
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Predictor copy", True))
    w.copy_filter()
    copied = w._active_pid
    assert copied != pid and presets.get(copied)["params"]["png_prediction"] == "best"
    wait_until(lambda: not w._artifacts.pending)
    copied_result = w._artifacts.results[w._result_key(copied)]
    assert Path(copied_result.pdf_path).read_bytes() == Path(result.pdf_path).read_bytes()
    assert copied_result.pdf_path != result.pdf_path and len(starts) == 1
    stored = next(p for p in w._custom_store().value("customPresets") if p["id"] == copied)
    assert preset_spec(stored)["png_prediction"] == "best"
    w.close()
    wait_until(lambda: not w._jobs)
    presets.PRESETS[:] = copy.deepcopy(_defaults)
    loaded = ui.MainWindow(None)
    try:
        choose(loaded, copied)
        assert loaded.png_prediction.isEnabled() and loaded.png_prediction.currentData() == "best"
        assert not loaded._draft_specs
    finally:
        loaded.close()


@pytest.mark.parametrize("choice", ["cancel", "discard", "save_as"])
def test_prediction_edits_use_the_existing_unsaved_switch_resolution(window, monkeypatch, choice):
    w = window
    choose(w, "bw-t180")
    w.compression.setCurrentIndex(w.compression.findData("bw-flate"))
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    w.save_filter()
    w.png_prediction.setCurrentIndex(w.png_prediction.findData("on"))
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Prediction saved copy", True))
    w.preset.setCurrentIndex(w.preset.findData("color-max"))
    if choice == "cancel":
        assert w._active_pid == "bw-t180" and w.png_prediction.currentData() == "on"
        assert w._draft_specs
    elif choice == "discard":
        assert w._active_pid == "color-max" and not w._draft_specs
        assert w._saved_specs["bw-t180"]["png_prediction"] == "off"
    else:
        assert w._active_pid not in ("bw-t180", "color-max")
        assert presets.get(w._active_pid)["params"]["png_prediction"] == "on"
        assert not w._draft_specs


@pytest.mark.parametrize("choice", ["cancel", "discard", "save_as"])
def test_algorithm_changes_obey_existing_switch_transaction(window, monkeypatch, choice):
    w = window
    choose(w, "bw-t180")
    original_mode = w._saved_specs["bw-t180"]["mode"]
    original_uuid = presets.get("bw-t180")["uuid"]
    w.compression.setCurrentIndex(w.compression.findData("bw-flate"))
    w.stream_compression.setCurrentIndex(w.stream_compression.findData("zopfli"))
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    draft = w._artifacts.results[w._result_key("bw-t180")]
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda pid: choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Explicit codec copy", True))
    w.preset.setCurrentIndex(w.preset.findData("color-max"))
    assert w._saved_specs["bw-t180"]["mode"] == original_mode
    assert presets.get("bw-t180")["uuid"] == original_uuid
    if choice == "cancel":
        assert w._active_pid == "bw-t180" and w.compression.currentData() == "bw-flate"
        assert w.stream_compression.currentData() == "zopfli" and "bw-t180" in w._draft_specs
        assert os.path.isfile(draft.pdf_path)
    elif choice == "discard":
        assert w._active_pid == "color-max" and not w._draft_specs
    else:
        assert w._active_pid not in ("bw-t180", "color-max")
        assert w.compression.currentData() == "bw-flate"
        assert w.stream_compression.currentData() == "zopfli" and not w._draft_specs
        copied = presets.get(w._active_pid)
        assert copied["mode"] == "bw-flate" and copied["uuid"] != original_uuid
        assert copied["params"]["stream_compression"] == "zopfli"
        assert w._saved_specs[w._active_pid]["mode"] == "bw-flate"


@pytest.mark.parametrize("pid,field", [("color-max", "jpeg_q"), ("color-j2k", "jpx_q")])
def test_quality_slider_spinner_use_one_debounce_and_saved_file_lifecycle(window, monkeypatch, pid, field):
    w = window
    choose(w, pid)
    assert w.quality_control.isEnabled() and w.quality_value.value() == 75
    uid = presets.get(pid)["uuid"]
    starts = []
    start = w._artifacts.start

    def record(key, path, spec, *args, **kwargs):
        copying = key in w._artifacts.copy_sources
        worker = start(key, path, spec, *args, **kwargs)
        if worker is not None and not copying:
            starts.append(dict(spec))
        return worker

    monkeypatch.setattr(w._artifacts, "start", record)
    w.quality_control.slider.setValue(89)
    w.quality_value.setFocus()
    w.quality_value.selectAll()
    QTest.keyClicks(w.quality_value, "86")
    w.quality_value.stepUp()
    assert w.quality_control.value() == w.quality_value.value() == 87
    assert w._spec_for(pid)[field] == 87 and not starts
    assert w._preview_timer.isActive() and w._filter_display_name(pid).endswith(" *")
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 1 and starts[0][field] == 87
    saved = w._artifacts.results[w._result_key(pid)]
    assert w.after._pdf_source.path == saved.pdf_path
    assert saved.nbytes == os.path.getsize(saved.pdf_path)
    assert "q87" in ui._preset_algo(pid, w._spec_for(pid))
    w.save_filter()
    assert not w._draft_specs
    assert presets.get(pid)["params"][field] == 87 and presets.get(pid)["uuid"] == uid
    w.quality_value.setValue(84)
    wait_until(lambda: not w._preview_timer.isActive() and not w._artifacts.pending)
    assert len(starts) == 2
    w.revert_filter()
    assert w.quality_value.value() == 87 and not w._draft_specs
    assert w._artifacts.results[w._result_key(pid)] is saved and len(starts) == 2
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Saved quality copy", True))
    w.copy_filter()
    copied = w._active_pid
    assert copied != pid and presets.get(copied)["params"][field] == 87
    wait_until(lambda: not w._artifacts.pending)
    duplicate = w._artifacts.results[w._result_key(copied)]
    assert Path(duplicate.pdf_path).read_bytes() == Path(saved.pdf_path).read_bytes()
    assert duplicate.pdf_path != saved.pdf_path and len(starts) == 2
    presets.PRESETS[:] = copy.deepcopy(_defaults)
    loaded = ui.MainWindow(None)
    try:
        choose(loaded, copied)
        assert loaded._spec_for(copied)[field] == 87
        assert loaded.quality_value.value() == 87 and not loaded._draft_specs
    finally:
        loaded.close()


def test_quality_is_disabled_and_ineffective_for_other_codecs_and_lossless(window):
    w = window
    choose(w, "bw-t180")
    key = w._result_key(w._active_pid)
    assert not w.quality_control.isEnabled() and not w.quality_label.isEnabled()
    w.quality_value.setValue(50)  # even programmatic disabled changes are no-ops
    assert not w._draft_specs and not w._preview_timer.isActive()
    assert w._result_key(w._active_pid) == key
    choose(w, "color-j2k")
    w.quality_value.setValue(88)
    w.lossless_box.setChecked(True)
    assert not w.quality_control.isEnabled()
    assert w._spec_for("color-j2k")["jpx_q"] == 88
    w.lossless_box.setChecked(False)
    assert w.quality_control.isEnabled() and w.quality_value.value() == 88
    w.revert_filter()


@pytest.mark.parametrize("pid,field", [("color-max", "jpeg_q"), ("color-j2k", "jpx_q")])
@pytest.mark.parametrize("choice", ["cancel", "discard", "save_as"])
def test_quality_edits_use_existing_unsaved_switch_transaction(window, monkeypatch, pid, field, choice):
    w = window
    choose(w, pid)
    w.quality_value.setValue(85)
    monkeypatch.setattr(w, "_ask_unsaved_filter", lambda current: choice)
    monkeypatch.setattr(QInputDialog, "getText", lambda *a, **k: ("Quality switch copy", True))
    w.preset.setCurrentIndex(w.preset.findData("bw-t180"))
    assert w._saved_specs[pid][field] == 75
    if choice == "cancel":
        assert w._active_pid == pid and w.quality_value.value() == 85
        assert pid in w._draft_specs
    elif choice == "discard":
        assert w._active_pid == "bw-t180" and not w._draft_specs
    else:
        assert w._active_pid not in (pid, "bw-t180") and not w._draft_specs
        assert w._spec_for(w._active_pid)[field] == 85
        assert w.quality_value.value() == 85
