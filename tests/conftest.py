"""pytest bootstrap: single-thread numerical backends before anything loads BLAS.

Background QThread workers abort under BLAS thread-pool load in constrained
environments (designer §37). Same guards live in pdf_minimalist/__main__.py
(app entry) and tools/shot.py.
"""
import os
import tempfile
import itertools
import pytest

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Isolate QSettings (§91 last-file memory): tests open throwaway PDFs through
# MainWindow, which must never overwrite the designer's real last file.
# NOTE: unconditional override (not setdefault) — this shell pre-exports
# XDG_CONFIG_HOME, which once silently defeated the isolation (issues.md B23).
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp(prefix="pdfmin-test-xdg-")


@pytest.fixture(autouse=True)
def isolate_gui_artifact_roots(request, tmp_path, monkeypatch):
    """Test windows may share a PID; production applications do not (§153).

    Give each constructed test window an isolated OS-temp root instead of
    adding test-only session layers to the production filesystem design.
    """
    if not request.module.__name__.endswith(("test_minis", "test_filter_lifecycle",
                                           "test_strip_reorder_identity")):
        return
    from pdf_minimalist.ui_qt import app as ui, paths
    store_type = ui.ArtifactStore
    counter = itertools.count()

    def new_store(_root):
        root = tmp_path / f"test-window-{next(counter)}" / "pdf-minimalist" / "saves"
        return store_type(str(root))

    original_sweep = paths.sweep_stale_temps
    monkeypatch.setattr(ui, "ArtifactStore", new_store)
    monkeypatch.setattr(paths, "sweep_stale_temps",
                        lambda *a, **kw: original_sweep(*a, temp_base=str(tmp_path), **kw))
