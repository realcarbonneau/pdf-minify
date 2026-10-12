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
    assert w._mini_job is not None or w._work_job is not None
    w.close()  # must not raise, hang, or abort
    t0 = time.perf_counter()
    while any(not j.isFinished() for j in list(w._jobs)):
        assert time.perf_counter() - t0 < 60, "worker did not stop"
        _app.processEvents()
        time.sleep(0.05)
    _app.processEvents()


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
