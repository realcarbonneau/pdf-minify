"""Lossless native PDF stream codecs, independent of bitmap encoding (§205)."""

from pathlib import Path
import subprocess
import tempfile
import time
import zlib

import pymupdf as fitz

from .cancel import CancelToken
from .external_tools import find_tool
from .pdf_io import CancelledError, FITZ_LOCK

STREAM_POLICIES = (
    ("flate", "Flate"),
    ("zopfli", "Flate (Zopfli, slow)"),
    ("brotli", "Brotli (limited support)"),
    ("best", "Best (Zopfli/Brotli)"),
)
STREAM_LABELS = dict(STREAM_POLICIES)
DEFAULT_STREAM_POLICY = "flate"
_BROTLI_EXTENSION_URL = "https://pdfa.org/resource/extension-brotli"


def permits_brotli(policy):
    """Policies whose result can require a Brotli-capable PDF reader."""
    return policy in ("brotli", "best")


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
    binary = find_tool("zopfli")
    if binary is None:
        raise RuntimeError("Zopfli is not installed; choose Flate or install zopfli.")
    with tempfile.TemporaryDirectory(prefix="native-zopfli-", dir=directory) as scratch:
        source = Path(scratch) / "stream"
        source.write_bytes(data)
        process = subprocess.Popen([binary, "--zlib", "-c", str(source)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            while True:
                check_cancel(token)
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
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    root, extensions, previous = _brotli_extension_objects(doc)
    if m.pdf_version(native) < 20:
        doc.xref_set_key(doc.pdf_catalog(), "Version", "/2.0")
    if brotli_declaration_present(doc):
        return
    if not m.pdf_is_dict(extensions):
        extensions = m.pdf_new_dict(native, 1)
        m.pdf_dict_puts(root, "Extensions", extensions)
    entry = m.pdf_new_dict(native, 5)
    for key, value in (("Type", m.pdf_new_name("DeveloperExtensions")),
                       ("BaseVersion", m.pdf_new_name("2.0")),
                       ("ExtensionLevel", m.pdf_new_int(1)),
                       ("ExtensionRevision", m.pdf_new_text_string("2026")),
                       ("URL", m.pdf_new_text_string(_BROTLI_EXTENSION_URL))):
        m.pdf_dict_puts(entry, key, value)
    if m.pdf_is_array(previous):
        m.pdf_array_push(previous, entry)
    elif not m.pdf_is_null(previous):
        entries = m.pdf_new_array(native, 2)
        m.pdf_array_push(entries, previous)
        m.pdf_array_push(entries, entry)
        m.pdf_dict_puts(extensions, "PDFa", entries)
    else:
        m.pdf_dict_puts(extensions, "PDFa", entry)


def _brotli_extension_objects(doc):
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    root = m.pdf_dict_gets(m.pdf_trailer(native), "Root")
    extensions = m.pdf_dict_gets(root, "Extensions")
    return root, extensions, m.pdf_dict_gets(extensions, "PDFa")


def _is_brotli_declaration(entry):
    m = fitz.mupdf
    return bool(m.pdf_is_dict(entry) and
                m.pdf_to_text_string(m.pdf_dict_gets(entry, "URL")) == _BROTLI_EXTENSION_URL)


def brotli_declaration_present(doc):
    """Recognize only Brotli's entry, including indirect dictionaries/arrays."""
    m = fitz.mupdf
    with FITZ_LOCK:
        _, _, entry = _brotli_extension_objects(doc)
        return (any(_is_brotli_declaration(m.pdf_array_get(entry, i))
                    for i in range(m.pdf_array_len(entry))) if m.pdf_is_array(entry)
                else _is_brotli_declaration(entry))


def set_brotli_declaration(doc, enabled=False):
    """Opt-in metadata; remove only Brotli entries, never other extensions.

    Do not downgrade source PDF versions: an inherited /Version may describe
    unrelated PDF 2.0 features, not just a former Brotli declaration.
    """
    with FITZ_LOCK:
        if enabled:
            _declare_brotli(doc)
            return
        m = fitz.mupdf
        root, extensions, entry = _brotli_extension_objects(doc)
        removed = False
        if m.pdf_is_array(entry):
            for i in reversed(range(m.pdf_array_len(entry))):
                if _is_brotli_declaration(m.pdf_array_get(entry, i)):
                    m.pdf_array_delete(entry, i)
                    removed = True
            if removed and not m.pdf_array_len(entry):
                m.pdf_dict_dels(extensions, "PDFa")
        elif _is_brotli_declaration(entry):
            m.pdf_dict_dels(extensions, "PDFa")
            removed = True
        if removed and not m.pdf_dict_len(extensions):
            m.pdf_dict_dels(root, "Extensions")


def recompress_native_streams(doc, policy, *, directory=None, token=None,
                              brotli_declaration=False):
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
        set_brotli_declaration(doc, brotli_declaration)
    return dict(streams=count, raw_bytes=raw_total, encoded_bytes=encoded_total,
                encode_seconds=time.perf_counter()-started)
