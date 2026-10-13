import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pdf_minimalist.ui_qt.app import MainWindow  # noqa: E402
from pdf_minimalist.ui_qt.jobs import cpu_cap, estimate_bytes, mini_for_preset  # noqa: E402
from pdf_minimalist.ui_qt.jobs import render_gray  # noqa: E402

_app = QApplication.instance() or QApplication([])


def _three_pages(tmpdir):
    src = os.path.join(tmpdir, "m.pdf")
    d = fitz.open()
    for i in range(3):
        p = d.new_page(width=400, height=400)
        p.insert_text((50, 200), f"Mini test {i}")
    d.save(src)
    d.close()
    return src


def _wait_job(w, timeout=90):
    # Queued cross-thread results can land after isFinished flips, so settle
    # on the STORES (minis + amounts for every filter), not thread state.
    t0 = time.perf_counter()
    while len(w._mini_view) < len(w._strip_ids) or len(w._mini_est) < len(w._strip_ids):
        assert time.perf_counter() - t0 < timeout, "filter results hung"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


def test_background_job_fills_minis_and_preview(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    assert w.before.page_count == 3
    _wait_job(w)
    assert w.after.page_count == 3  # preview applied without freezing
    assert w.filters.count() == 10  # passthrough/Original has no mini (§30)
    for i in range(10):
        assert not w.filters.item(i).icon().isNull(), i
    assert len(w._mini_est) == 10
    # every filter must hold a real reframed composite, not a placeholder:
    # placeholders pass icon checks and hid the JPX mini crash (§56 wiring).
    assert set(w._mini_view) == set(w._strip_ids)
    for pid, arr in w._mini_view.items():
        assert arr.ndim == 3 and arr.shape[2] == 3, pid
    # §§55/59/61: all captions are real post-save amounts with % — no "est.".
    for pid, v in w._mini_est.items():
        assert any(u in v for u in ("B", "KB", "MB")), (pid, v)
        assert not v.startswith("est."), (pid, v)
        assert "%" in v, (pid, v)


def test_pure_job_helpers():
    assert cpu_cap() >= 1
    gray = render_gray("examples/images.pdf", 0, 150)
    assert gray.ndim == 2
    from pdf_minimalist.ui_qt.jobs import to_mini, crop_view
    mini = mini_for_preset(to_mini(crop_view(gray, None)), "bw-otsu")
    assert mini.shape == to_mini(gray).shape
    n = estimate_bytes("examples/images.pdf", 0, "bw-otsu", 300)
    assert n > 1000


def test_threshold_slider_only_for_simple(tmp_path):
    """Designer §65: T feeds Simple only — disabled (not lying) elsewhere."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    from pdf_minimalist.core import presets
    w.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index("bw-otsu"))
    assert not w.slider.isEnabled()  # otsu computes its own threshold
    w.strategy.setCurrentText("simple")
    assert w.slider.isEnabled()
    w.strategy.setCurrentText("sauvola")
    assert not w.slider.isEnabled()


def test_lossless_checkbox_states(tmp_path):
    """Designer §100: choice only for JPX; grey + fixed everywhere else."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(ids.index("bw-otsu"))
    assert w.lossless_box.isChecked() and not w.lossless_box.isEnabled()
    w.preset.setCurrentIndex(ids.index("color-j2k"))
    assert w.lossless_box.isEnabled() and not w.lossless_box.isChecked()
    w.lossless_box.setChecked(True)
    assert w.lossless_box.isChecked()
    w.preset.setCurrentIndex(ids.index("color-max"))
    assert not w.lossless_box.isChecked() and not w.lossless_box.isEnabled()
    w.preset.setCurrentIndex(ids.index("color-i64"))
    assert w.lossless_box.isChecked() and not w.lossless_box.isEnabled()


def test_recompute_never_blanks_amounts(tmp_path):
    """Designer §106: stale-while-revalidate — a recompute keeps known
    amounts on screen (bars signal the work); only a new file clears."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    held = {pid: f"{i}KB ({i}%)" for i, pid in enumerate(w._strip_ids)}
    w._mini_est.update(held)
    w._reframe_minis()
    assert w._mini_est == held


def test_filter_set_covers_every_preset(tmp_path):
    """Designer complaint: every strip filter renders its own kind — BW minis
    are never color photos, and every preset previews + measures cleanly."""
    import numpy as _np
    from pdf_minimalist.core import presets
    from pdf_minimalist.ui_qt.jobs import (
        mini_page_task, preview_page, estimate_bytes, color_doc_total,
        PREVIEW_DPI, render_rgb)
    from pdf_minimalist.core.cancel import CancelToken
    src = str(_three_pages(str(tmp_path)))
    for p in presets.PRESETS:
        if p["mode"] == "passthrough":
            continue
        pid = p["id"]
        mini = mini_page_task(src, 0, pid)
        assert mini.ndim == 3 and mini.shape[2] == 3, pid
        if p["mode"] == "bw":
            # BW minis are achromatic (resampling fringes allowed) — never a
            # color photo.
            assert (mini[..., 0] == mini[..., 1]).all(), pid
            assert (mini[..., 1] == mini[..., 2]).all(), pid
        if p["mode"] == "bw":
            assert estimate_bytes(src, 0, pid, 300, True) > 0, pid
        else:
            assert color_doc_total(src, pid) >= 0, pid
        spec = {"preset_id": pid, "mode": p["mode"], "dpi": 300,
                "strategy": "otsu", "t": 180, "colors": 64,
                "dpi_cap": 150, "rate": 192, "lossless": False,
                "force_raster": False}
        prev = preview_page(src, 0, spec)
        assert prev.ndim == 3 and prev.shape[2] == 3, pid


def test_preview_ignores_force_raster(tmp_path):
    """Designer §113: the right pane always shows the filter effect —
    toggling force must not rebuild (or change) the preview."""
    import numpy as _np
    from pdf_minimalist.ui_qt.jobs import preview_page
    from pdf_minimalist.ui_qt.app import MainWindow as _MW
    src = str(_three_pages(str(tmp_path)))
    base = {"preset_id": "bw-otsu", "mode": "bw", "dpi": 300,
            "strategy": "otsu", "t": 180}
    a = preview_page(src, 0, dict(base, force_raster=True))
    b = preview_page(src, 0, dict(base, force_raster=False))
    assert _np.array_equal(a, b)
    assert _MW._spec_tuple(dict(base, force_raster=True)) == \
        _MW._spec_tuple(dict(base, force_raster=False))


def test_colors_slider_only_for_indexed(tmp_path):
    """Designer §67: Colors feeds Indexed only — disabled elsewhere."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index("color-i64"))
    assert w.colors.isEnabled()
    assert w.colors.value() == 64
    w.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index("bw-otsu"))
    assert not w.colors.isEnabled()
    w.colors.setValue(16)
    w.preset.setCurrentIndex([p["id"] for p in presets.PRESETS].index("color-p16"))
    assert w.colors.value() == 16  # preset default lands on switch


def test_zoom_actions_have_real_icons():
    """Designer §84: zoom magnifiers are drawn in code, never theme-missing."""
    from pdf_minimalist.ui_qt.app import MainWindow as _MW
    w = _MW(None)
    for act in (w.zoom_in_act, w.zoom_out_act):
        assert not act.icon().isNull()
        assert not act.icon().pixmap(16, 16).isNull()


def test_details_codec_first_for_all_modes():
    """Designer §82: Codec opens the details in every mode, same sequence."""
    from pdf_minimalist.core import presets
    w = MainWindow(None)
    for p in presets.PRESETS:
        w.preset.setCurrentIndex([q["id"] for q in presets.PRESETS].index(p["id"]))
        first = w.details.text().splitlines()[0]
        assert first.startswith("Codec:"), (p["id"], first)


def test_preset_owns_its_dpi(tmp_path):
    """Designer §§83/85: one DPI — presets seed the shared combo, which rules."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(ids.index("bw-fast"))
    assert w.dpi.currentData() == 200 and w.dpi.isEnabled()
    w.preset.setCurrentIndex(ids.index("color-j2k"))
    assert w.dpi.isEnabled()  # the single DPI feeds every mode
    assert w.dpi.currentData() == 150  # preset cap seeds the combo
    w.preset.setCurrentIndex(ids.index("bw-otsu"))
    assert w.dpi.currentData() == 300 and w.dpi.isEnabled()


def test_zoom_combo_two_way(tmp_path):
    """Designer §86: preset pick, typed number, and live sync all work."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.zoom_combo.setCurrentIndex(5)  # 150%
    w._zoom_combo_chosen(5)
    assert abs(w.before._zoom - 1.5) < 1e-9
    assert w.after._zoom == w.before._zoom
    w.zoom_combo.setCurrentText("42")
    w._zoom_combo_chosen()
    assert abs(w.before._zoom - 0.42) < 1e-9
    w.before.set_zoom(2.0)
    w._update_zoom_control()
    assert w.zoom_combo.currentText() == "200%"


def test_right_pane_zoom_reframes_minis(tmp_path):
    """Designer §92: zooming the RIGHT pane notifies, and the trailing
    debounce reframes minis to the last view (no stuck frames)."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    pid = w._strip_ids[0]
    before = w._mini_view[pid].tobytes()
    w.after.set_zoom(w.after._zoom * 2.0)
    t0 = time.perf_counter()
    while time.perf_counter() - t0 < 5:
        _app.processEvents()
        time.sleep(0.05)
        if w._mini_view[pid].tobytes() != before:
            break
    assert w._mini_view[pid].tobytes() != before


def test_close_mid_processing_is_safe(tmp_path):
    """Designer §94: closing while workers run must never crash."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _app.processEvents()
    assert w._mini_jobs or w._work_job is not None
    w.close()  # must not raise, hang, or abort
    t0 = time.perf_counter()
    while any(not j.isFinished() for j in list(w._jobs)):
        assert time.perf_counter() - t0 < 60, "worker did not stop"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


def test_filter_progress_weights_cost(tmp_path):
    """Designer §§89/95: bars start at 0, minis weigh ~15%, amounts ~85%."""
    from pdf_minimalist.ui_qt.app import filter_progress
    assert filter_progress(0, 7, 0, 7) == 0.0
    first_mini = filter_progress(1, 7, 0, 7)
    assert 0.0 < first_mini < 0.2, first_mini  # never near half
    assert filter_progress(7, 7, 0, 7) < 0.5
    assert filter_progress(7, 7, 7, 7) == 1.0
    assert filter_progress(0, 0, 0, 0) == 1.0
    assert filter_progress(0, 0, 3, 7) == 3 / 7


def test_panes_equal_no_splitter(tmp_path):
    """Designer §107: no splitter — fixed equal layout, widths always match."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    assert hasattr(w, "panes") and not hasattr(w, "split")
    assert abs(w.before.width() - w.after.width()) <= 2, \
        (w.before.width(), w.after.width())


def test_preset_strip_sync_by_id():
    import tempfile
    src = os.path.join(tempfile.mkdtemp(), "m.pdf")
    d = fitz.open()
    p = d.new_page(width=400, height=400)
    p.insert_text((50, 200), "Sync test")
    d.save(src)
    d.close()
    w = MainWindow(src)
    w.preset.setCurrentIndex(0)  # orig/passthrough: no strip row follows
    assert w.preset.itemData(0) == "orig"
    w._filterstrip_chosen(0)  # first mini -> bw-otsu preset
    from pdf_minimalist.core import presets
    assert w.preset.itemData(w.preset.currentIndex()) == presets.PRESETS[1]["id"]


def test_file_menu_and_single_panel(tmp_path):
    w = MainWindow(str(_three_pages(str(tmp_path))))
    names = [a.text() for a in w.menuBar().actions()]
    assert "&File" in names and "&View" in names
    assert w.before.page_count == 3  # baseline renders synchronously
    _wait_job(w)
    assert w.after.page_count == 3  # preview arrives via background job


def test_force_raster_per_filter(tmp_path):
    """Designer §103: only bw-fast forces; preset switch syncs the box."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    forced = [p["id"] for p in presets.PRESETS
              if p["mode"] == "bw" and p["params"].get("force_raster")]
    assert forced == ["bw-fast"]
    w.preset.setCurrentIndex(ids.index("bw-otsu"))
    assert not w.force_raster.isChecked()
    w.preset.setCurrentIndex(ids.index("bw-fast"))
    assert w.force_raster.isChecked()


def test_zz_rename_and_copy_filter(tmp_path, monkeypatch):
    """Designer §109: rename + copy via naming popup, persisted. Last."""
    from PySide6.QtWidgets import QInputDialog
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    n_combo, n_strip = w.preset.count(), w.filters.count()
    monkeypatch.setattr(QInputDialog, "getText",
                        staticmethod(lambda *a, **k: ("My Otsu", True)))
    w.preset.setCurrentIndex(ids.index("bw-otsu"))
    w.rename_filter()
    assert presets.get("bw-otsu")["label"] == "My Otsu"
    assert w.preset.itemText(w.preset.currentIndex()) == "My Otsu"
    monkeypatch.setattr(QInputDialog, "getText",
                        staticmethod(lambda *a, **k: ("J2K copy", True)))
    w.preset.setCurrentIndex(ids.index("color-j2k"))
    w.copy_filter()
    assert w.preset.count() == n_combo + 1
    assert w.filters.count() == n_strip + 1
    assert w._strip_ids[-1] not in ids
    assert presets.get(w._strip_ids[-1])["mode"] == "jpx"


def test_preview_only_status_and_panel_divider(tmp_path):
    """Designer §§107/115/117: preview-only work says preview; the divider
    between the previews and the right panel drags (slider gone), and the
    two panes stay locked equal."""
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    fkey = w._file_key()
    pkey = (fkey, w._spec_tuple(w._active_spec()))
    w._preview_cache.pop(pkey, None)  # force a preview-only miss
    w._dispatch_filters()
    assert w.status.text().startswith("Rendering preview"), w.status.text()
    assert not hasattr(w, "pw_slider")  # slider removed, divider rules
    assert hasattr(w, "panel_split") and not hasattr(w, "split")
    w.resize(1100, 650)
    w.show()
    _app.processEvents()
    before = w.panel_split.sizes()
    assert len(before) == 2
    w.panel_split.setSizes([before[0] + 120, max(200, before[1] - 120)])
    _app.processEvents()
    assert w.panel_split.sizes() != before  # divider really moved
    assert abs(w.before.width() - w.after.width()) <= 2  # panes still equal
    from pdf_minimalist.ui_qt.app import _rename_icon, _copy_icon
    assert not _rename_icon().isNull() and not _copy_icon().isNull()


def test_force_toggle_updates_no_filter(tmp_path):
    """Designer §§105/106/113 + repeated complaint: flipping "Force
    full-page raster" arms Save and refreshes details only — no mini, amount
    or preview job may launch and no shown size may move."""
    import time
    w = MainWindow(str(_three_pages(str(tmp_path))))
    _wait_job(w)
    before_est = dict(w._mini_est)
    before_view = {pid: arr.tobytes() for pid, arr in w._mini_view.items()}
    before_details = w.details.text()
    gen_before = w._gen
    w.force_raster.toggle()
    assert "text pass-through" in w.details.text() or "forced raster" in w.details.text()
    assert w.details.text() != before_details  # details DO reflect it
    # Settle to idle first: a slow initial job may still own the status
    # line — the point is the toggle itself must not ADD any job.
    t0 = time.perf_counter()
    while (any(not j.isFinished() for j in w._mini_jobs)
           or (w._work_job is not None and not w._work_job.isFinished())
           or w.status.text().startswith("Rendering")):
        assert time.perf_counter() - t0 < 120, "jobs never went idle"
        _app.processEvents()
        time.sleep(0.05)
    assert w._gen == gen_before  # the toggle dispatched zero jobs
    assert dict(w._mini_est) == before_est
    assert {pid: arr.tobytes() for pid, arr in w._mini_view.items()} == before_view


def test_zz_save_filter_persists_and_invalidates(tmp_path):
    """Designer §112: Save writes UI settings into the filter and rebuilds."""
    from pdf_minimalist.core import presets
    w = MainWindow(str(_three_pages(str(tmp_path))))
    ids = [p["id"] for p in presets.PRESETS]
    w.preset.setCurrentIndex(ids.index("bw-t180"))
    w.slider.setValue(210)
    w.save_filter()
    assert presets.get("bw-t180")["params"]["t"] == 210
    store = w._custom_store().value("customPresets", [])
    assert any(c.get("id") == "bw-t180" for c in store)
    # caches for the new recipe are dropped so they rebuild
    fkey = w._file_key()
    assert all(k[1] != "bw-t180" for k in w._mini_pages)
