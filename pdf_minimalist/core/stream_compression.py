"""Lossless native PDF stream codecs, independent of bitmap encoding (§205)."""

from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import zlib

import pymupdf as fitz

from .cancel import CancelToken
from .pdf_io import CancelledError, FITZ_LOCK

STREAM_POLICIES = (
    ("flate", "Flate"),
    ("zopfli", "Flate (Zopfli, slow)"),
    ("brotli", "Brotli (limited support)"),
)
STREAM_LABELS = dict(STREAM_POLICIES)
DEFAULT_STREAM_POLICY = "flate"


def check_cancel(token):
    if token.cancelled:
        raise CancelledError()


def brotli_available():
    m = fitz.mupdf
    return all(hasattr(m, name) for name in (
        "fz_new_brotli_data_from_buffer", "FZ_BROTLI_BEST", "fz_new_buffer_from_data"))


def _brotli(data, level):
    if not brotli_available():
        raise RuntimeError("This MuPDF build has no Brotli encoder; choose Flate.")
    m = fitz.mupdf
    with FITZ_LOCK:
        source = m.fz_new_buffer_from_copied_data(data)
        pointer, size = m.fz_new_brotli_data_from_buffer(source, level)
        # Transfer the allocated native block into an owning buffer before
        # extracting Python bytes. No leaked SWIG raw allocation per stream.
        encoded = m.fz_new_buffer_from_data(pointer, size)
        return m.fz_buffer_extract(encoded)


def _zopfli(data, directory, token):
    binary = shutil.which("zopfli")
    if binary is None:
        raise RuntimeError("Zopfli is not installed; choose Flate or install zopfli.")
    with tempfile.TemporaryDirectory(prefix="native-zopfli-", dir=directory) as scratch:
        source = Path(scratch) / "stream"
        source.write_bytes(data)
        process = subprocess.Popen([binary, "--zlib", "-c", str(source)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        started = time.monotonic()
        try:
            while True:
                check_cancel(token)
                if time.monotonic() - started > 120:
                    raise RuntimeError("Zopfli stream encoding exceeded 120 seconds.")
                try:
                    encoded, error = process.communicate(timeout=.05)
                    break
                except subprocess.TimeoutExpired:
                    pass
        except BaseException:
            process.terminate()
            try:
                process.communicate(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
            raise
        if process.returncode or not encoded or zlib.decompress(encoded) != data:
            raise RuntimeError(f"Zopfli encoding failed: {error.decode(errors='replace')}")
        return encoded


def _run_length(data):
    """PDF RunLengthDecode transport, benchmark legacy baseline only."""
    output = bytearray()
    start = 0
    while start < len(data):
        count = 1
        while count < 128 and start+count < len(data) and data[start+count] == data[start]:
            count += 1
        if count >= 3:
            output.extend((257-count, data[start]))
            start += count
        else:
            end = start+1
            while end < len(data) and end-start < 128:
                if end+2 < len(data) and data[end] == data[end+1] == data[end+2]:
                    break
                end += 1
            output.append(end-start-1)
            output.extend(data[start:end])
            start = end
    output.append(128)
    return bytes(output)


def _lzw(data):
    """PDF LZW with EarlyChange=1; benchmark historical baseline only."""
    output = bytearray()
    accumulator = bits = 0
    width, decoder_next, previous = 9, 258, False

    def emit(code):
        nonlocal accumulator, bits, width, decoder_next, previous
        accumulator = (accumulator << width) | code
        bits += width
        while bits >= 8:
            bits -= 8
            output.append((accumulator >> bits) & 255)
        accumulator &= (1 << bits)-1
        if code == 256:
            width, decoder_next, previous = 9, 258, False
        elif code != 257:
            if previous:
                decoder_next += 1
                if width < 12 and decoder_next == (1 << width)-1:
                    width += 1
            previous = True

    dictionary = {bytes((byte,)): byte for byte in range(256)}
    next_code = 258
    emit(256)
    prefix = b""
    for byte in data:
        character = bytes((byte,))
        candidate = prefix+character
        if candidate in dictionary:
            prefix = candidate
            continue
        emit(dictionary[prefix])
        dictionary[candidate] = next_code
        next_code += 1
        if next_code == 4096:
            emit(256)
            dictionary = {bytes((byte,)): byte for byte in range(256)}
            next_code = 258
        prefix = character
    if prefix:
        emit(dictionary[prefix])
    emit(257)
    if bits:
        output.append(accumulator << (8-bits))
    return bytes(output)


def encode_stream(data, policy, *, directory=None, token=None):
    """Return stored bytes/filter. Extra legacy policies are benchmark-only."""
    token = token or CancelToken()
    check_cancel(token)
    if policy not in ("flate", "flate-fast", "zopfli", "brotli", "brotli-9", "lzw", "runlength", "none"):
        raise ValueError(f"Unknown PDF stream compression: {policy}")
    # No samples need no filter. Besides needless overhead, MuPDF 1.28.2's
    # Brotli encoder returns zero bytes for an empty input (no end marker),
    # which can loop forever in its decoder. Never construct that invalid PDF.
    if not data:
        return b"", None
    if policy in ("flate", "flate-fast"):
        return zlib.compress(data, 9 if policy == "flate" else 1), "/FlateDecode"
    if policy == "zopfli":
        return _zopfli(data, directory, token), "/FlateDecode"
    if policy in ("brotli", "brotli-9"):
        return _brotli(data, 11 if policy == "brotli" else 9), "/BrotliDecode"
    if policy == "lzw":
        return _lzw(data), "/LZWDecode"
    if policy == "runlength":
        return _run_length(data), "/RunLengthDecode"
    if policy == "none":
        return data, None
    raise ValueError(f"Unknown PDF stream compression: {policy}")


def native_stream_xrefs(doc):
    """Non-image resources/content only, not attachments/metadata/container."""
    for xref in range(1, doc.xref_length()):
        if not doc.xref_is_stream(xref):
            continue
        if doc.xref_get_key(xref, "Subtype")[1] == "/Image":
            continue
        if doc.xref_get_key(xref, "Type")[1] in (
                "/ObjStm", "/XRef", "/EmbeddedFile", "/Metadata"):
            continue
        yield xref


def _declare_brotli(doc):
    catalog = doc.pdf_catalog()
    doc.xref_set_key(catalog, "Version", "/2.0")
    entry = ("<< /Type /DeveloperExtensions /BaseVersion /2.0 /ExtensionLevel 1 "
             "/ExtensionRevision (2026) /URL (https://pdfa.org/resource/extension-brotli) >>")
    kind, previous = doc.xref_get_key(catalog, "Extensions/PDFa")
    if kind == "xref":
        previous = doc.xref_object(int(previous.split()[0]))
    if "https://pdfa.org/resource/extension-brotli" in previous:
        return
    if kind != "null":
        previous = previous.strip()
        entry = (previous[:-1]+" "+entry+"]" if previous.startswith("[")
                 else "["+previous+" "+entry+"]")
    doc.xref_set_key(catalog, "Extensions/PDFa", entry)


def recompress_native_streams(doc, policy, *, directory=None, token=None):
    """Exact per-stream readback before the one final PDF/container save."""
    token = token or CancelToken()
    count = raw_total = encoded_total = 0
    started = time.perf_counter()
    with FITZ_LOCK:
        for xref in list(native_stream_xrefs(doc)):
            check_cancel(token)
            previous_warnings = fitz.TOOLS.mupdf_warnings(reset=False)
            data = doc.xref_stream(xref)
            if fitz.TOOLS.mupdf_warnings(reset=False) != previous_warnings:
                raise RuntimeError(f"Native stream {xref} failed source decoding.")
            encoded, filtr = encode_stream(data, policy, directory=directory, token=token)
            check_cancel(token)
            doc.update_stream(xref, encoded, compress=False)
            doc.xref_set_key(xref, "Filter", filtr or "null")
            doc.xref_set_key(xref, "DecodeParms", "null")
            if (doc.xref_stream(xref) != data or
                    fitz.TOOLS.mupdf_warnings(reset=False) != previous_warnings):
                raise RuntimeError(f"Native stream {xref} failed exact {policy} readback.")
            count += 1
            raw_total += len(data)
            encoded_total += len(encoded)
        if policy.startswith("brotli"):
            _declare_brotli(doc)
    return dict(streams=count, raw_bytes=raw_total, encoded_bytes=encoded_total,
                encode_seconds=time.perf_counter()-started)
