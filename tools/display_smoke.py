"""Real-file viewport pixel/zoom review (§§172–175), isolated GUI settings."""

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from PySide6.QtGui import QImage
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from pdf_minimalist.ui_qt.app import MainWindow, setup_logging


def main():
    with tempfile.TemporaryDirectory(prefix="pdfmin-display-settings-") as settings:
        os.environ["XDG_CONFIG_HOME"] = settings
        app = QApplication([])
        setup_logging()
        w = MainWindow(str(ROOT / "examples/images.pdf"))
        w.resize(1100, 650)
        w.show()

        def ready():
            deadline = time.monotonic() + 90
            while w._artifacts.pending or w._preview_timer.isActive():
                assert time.monotonic() < deadline
                app.processEvents()
                time.sleep(0.02)
            app.processEvents()
            assert not w._artifacts.errors, w._artifacts.errors

        ready()
        w.preset.setCurrentIndex(w.preset.findData("bw-otsu"))
        w.force_raster.setChecked(True)
        ready()
        artifact = w._artifacts.results[w._result_key("bw-otsu")]
        digest = hashlib.sha256(Path(artifact.pdf_path).read_bytes()).hexdigest()
        generation = w._gen
        out = ROOT / ".tmp"
        out.mkdir(exist_ok=True)
        suffix = f"{w.devicePixelRatioF():g}x"
        records = []
        for zoom in (0.1, 0.75, 2, 4):
            t0 = time.perf_counter()
            w.after.set_zoom(zoom)
            # Paint immediately for a measured native readback, then settle
            # the ordinary trailing mini framing before review captures.
            app.processEvents()
            paint_ms = (time.perf_counter() - t0) * 1000
            QTest.qWait(220)
            w._reframe_minis()
            assert w.before.cols() == w.after.cols()
            assert not w._artifacts.pending and w._gen == generation
            assert not w._preview_timer.isActive()
            assert hashlib.sha256(Path(artifact.pdf_path).read_bytes()).hexdigest() == digest
            prefix = out / f"display-{suffix}-zoom-{zoom:g}"
            w.grab().save(str(prefix) + ".png")
            w.before.viewport().grab().save(str(prefix) + "-original.png")
            shot = w.after.viewport().grab().toImage()
            shot.save(str(prefix) + "-preview.png")
            w.filters.viewport().grab().save(str(prefix) + "-strip.png")
            image = shot.convertToFormat(QImage.Format_RGBA8888)
            pixels = np.frombuffer(image.constBits(), dtype=np.uint8).reshape(
                image.height(), image.bytesPerLine() // 4, 4)[:, :image.width(), :3]
            item = w.after._items[0]
            visible = w.after.mapFromScene(item.sceneBoundingRect()).boundingRect().intersected(
                w.after.viewport().rect()).adjusted(2, 2, -2, -2)
            ratio = shot.devicePixelRatio()
            page = pixels[int(visible.top()*ratio):int((visible.bottom()+1)*ratio),
                          int(visible.left()*ratio):int((visible.right()+1)*ratio)]
            samples = [int(v) for v in np.unique(page)]
            assert page.size and set(samples) <= {0, 255}, samples
            record = dict(zoom=zoom, dpr=ratio, viewport_paint_ms=round(paint_ms, 2),
                          displayed_samples=samples, filter_generation=generation,
                          file_sha256=digest)
            records.append(record)
            print(record, flush=True)
        (out / f"display-{suffix}-metrics.json").write_text(json.dumps(records, indent=2))
        # This tool owns its isolated draft; never operates on designer edits.
        w._discard_filter("bw-otsu")
        w.close()
        app.processEvents()
        assert w.before._pdf_source is None and w.after._pdf_source is None
        print("EXACT DISPLAY GUI SMOKE GREEN", flush=True)


if __name__ == "__main__":
    main()
