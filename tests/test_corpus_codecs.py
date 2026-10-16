"""B115: stored PDF image filters, not decoded/extracted image formats."""

import builtins
from pathlib import Path
import re
from types import SimpleNamespace

import pymupdf as fitz
import pytest

from tools.corpus import fetch_and_validate as corpus


@pytest.mark.parametrize("source,expected", [
    ("examples/scan-jfk-poor-copies.pdf", "JBIG2"),
    ("examples/scan-naca-tm972.pdf", "CCITT"),
    ("examples/scan-naca-formulas.pdf", "CCITT"),
    ("examples/images.pdf", "Flate"),
    ("examples/models-nasa-tess.pdf", "JPEG"),
    ("examples/form-fw9.pdf", "none"),
])
def test_actual_corpus_encoding_never_uses_export_format(monkeypatch, source, expected):
    def forbidden(*args, **kwargs):
        pytest.fail("Extraction can change image format and cannot identify the stored codec")
    monkeypatch.setattr(fitz.Document, "extract_image", forbidden)
    assert corpus.codecs_of(source) == expected


@pytest.mark.parametrize("compress,expected", [(True, "Flate-1bit"), (False, "Raw-1bit")])
def test_flate_one_bit_is_not_confused_with_other_bilevel_formats(tmp_path, compress, expected):
    source = tmp_path / "one-bit.pdf"
    with fitz.open() as pdf:
        page = pdf.new_page(width=64, height=64)
        xref = pdf.get_new_xref()
        pdf.update_object(xref, "<< /Type /XObject /Subtype /Image /Width 64 /Height 64 "
                          "/BitsPerComponent 1 /ColorSpace /DeviceGray >>")
        pdf.update_stream(xref, b"\xAA" * 512, compress=compress)
        page.insert_image(page.rect, xref=xref)
        pdf.save(source)
    assert corpus.codecs_of(source) == expected


def test_poppler_fallback_reads_encoding_not_y_ppi(monkeypatch):
    original_import = builtins.__import__
    def without_pymupdf(name, *args, **kwargs):
        if name == "pymupdf":
            raise ImportError("exercise optional-reader fallback")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", without_pymupdf)
    monkeypatch.setattr(corpus.shutil, "which", lambda _: "/usr/bin/pdfimages")
    listing = ("page num type width height color comp bpc enc interp object ID x-ppi y-ppi size ratio\n"
               "--------------------------------------------------------------------------------\n"
               "1 0 image 2528 3290 gray 1 1 jbig2 no 14 0 300 300 16.5K 1.6%\n"
               "2 1 image 2304 3008 gray 1 1 ccitt no 8 0 300 300 37.4K 4.4%\n")
    monkeypatch.setattr(corpus.subprocess, "run", lambda *args, **kwargs: SimpleNamespace(stdout=listing))
    assert corpus.codecs_of("unused.pdf") == "CCITT,JBIG2"


def test_corpus_readme_inventory_matches_every_committed_pdf_filter():
    seen = set()
    for line in Path("examples/README.md").read_text().splitlines():
        match = re.match(r"\| `([^`]+\.pdf)` \|", line)
        if not match:
            continue
        source = Path("examples") / match[1]
        expected = line.split("|")[-2].strip()
        if expected.startswith("none"):
            expected = "none"
        assert corpus.codecs_of(source) == expected, source
        seen.add(source)
    assert seen == set(Path("examples").glob("*.pdf"))
