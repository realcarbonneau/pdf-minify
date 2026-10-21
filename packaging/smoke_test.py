"""Check a built Windows or macOS app before it is packaged or after install.

Usage: <bundled python> smoke_test.py APP_DIR [APP_COMMAND...]

APP_DIR is the folder holding `pdf_minify` and `bin`. APP_COMMAND starts the
app (the macOS app's executable); by default, this Python runs the
pdf-minify.pyw launcher in APP_DIR (Windows). Checks that every
import comes from the bundle, that MuPDF has Brotli, that the bundled jbig2
and zopfli run and encode, then starts the app (no window) on a PDF whose
name has a space and waits for it to show its first filtered preview. The
log is read while the app still runs: what its processes print as they are
stopped is not the app's.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time
import zlib
from pathlib import Path

APP_DIR = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(APP_DIR))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def check(condition, message):
    if not condition:
        sys.exit(f"FAILED: {message}")
    print(f"ok  {message}")


def stop(process):
    """Stop the app and the worker processes it started."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], capture_output=True)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


import numpy  # noqa: E402
import PIL  # noqa: E402
import PySide6  # noqa: E402
import pymupdf  # noqa: E402

import pdf_minify  # noqa: E402
from pdf_minify.core import external_tools, pipeline  # noqa: E402
from pdf_minify.core.stream_compression import brotli_available  # noqa: E402

print(f"pdf_minify {pdf_minify.__version__} | Python {sys.version.split()[0]} | PyMuPDF "
      f"{pymupdf.__version__} | PySide6 {PySide6.__version__} | NumPy {numpy.__version__} "
      f"| Pillow {PIL.__version__}")
check(Path(pdf_minify.__file__).resolve().is_relative_to(APP_DIR), "pdf_minify comes from the app")
check(brotli_available(), "MuPDF has Brotli")

jbig2, zopfli = pipeline.jbig2_binary(), pipeline.zopfli_binary()
bundled = external_tools.BUNDLED_BIN.resolve()
check(jbig2 is not None and Path(jbig2).resolve().parent == bundled, f"bundled jbig2: {jbig2}")
check(zopfli is not None and Path(zopfli).resolve().parent == bundled, f"bundled zopfli: {zopfli}")

data = b"PDF Minify " * 2000
sample = Path(tempfile.mkdtemp()) / "sample"
sample.write_bytes(data)
encoded = subprocess.run([zopfli, "--zlib", "-c", str(sample)], capture_output=True, timeout=120)
check(encoded.returncode == 0 and zlib.decompress(encoded.stdout) == data, "zopfli encodes")
gray = numpy.full((200, 300), 255, numpy.uint8)
gray[50:150, 40:260] = 0
payload = pipeline.bw_page_jbig2(gray)
check(payload is not None and len(payload) > 0, "jbig2 encodes")

# Start the app the way the launcher does, on a file whose name has a space.
work = Path(tempfile.mkdtemp())
pdf = work / "a file.pdf"
document = pymupdf.open()
document.new_page().insert_text((72, 72), "PDF Minify")
document.save(pdf)
if len(sys.argv) > 2:
    # The app runs in a scratch folder: make relative paths absolute.
    command = [str(Path(arg).absolute()) if Path(arg).exists() else arg for arg in sys.argv[2:]]
else:
    launcher = APP_DIR / "pdf-minify.pyw"
    check(launcher.exists(), f"launcher: {launcher}")
    command = [sys.executable, str(launcher)]
log = work / "app.log"
# The app sets up its own Python; only the display is chosen here.
env = {k: v for k, v in os.environ.items() if k not in ("PYTHONHOME", "PYTHONPATH")}
env["QT_QPA_PLATFORM"] = "offscreen"
with open(log, "w") as out:
    # Its own session (POSIX), so stop() reaches the workers too.
    app = subprocess.Popen(command + ["--debug", str(pdf)], stdout=out, stderr=subprocess.STDOUT,
                           cwd=work, env=env, start_new_session=os.name != "nt")
    deadline = time.time() + 120
    while time.time() < deadline and app.poll() is None:
        text = log.read_text(errors="replace")
        if "window shown" in text and "preview applied" in text:
            break
        time.sleep(1)
    time.sleep(2)  # an error being printed gets to finish
    running = app.poll() is None
    text = log.read_text(errors="replace")
    stop(app)
print(text[-6000:])
check(running, "the app is still running after opening the file")
check(f"opened {pdf}" in text, "the app opened the file")
check("window shown" in text, "the app showed its window")
check("preview applied" in text, "the app showed the file through a filter")
check("Traceback" not in text, "no errors in the app log")
print("SMOKE TEST PASSED")
