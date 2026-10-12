"""pytest bootstrap: single-thread numerical backends before anything loads BLAS.

Background QThread workers abort under BLAS thread-pool load in constrained
environments (designer §37). Same guards live in pdf_minimalist/__main__.py
(app entry) and tools/shot.py.
"""
import os
import tempfile

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

# Isolate QSettings (§91 last-file memory): tests open throwaway PDFs through
# MainWindow, which must never overwrite the designer's real last file.
os.environ.setdefault("XDG_CONFIG_HOME", tempfile.mkdtemp(prefix="pdfmin-test-xdg-"))
