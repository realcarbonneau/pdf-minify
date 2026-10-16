"""B112: structure links describe the actual native owners, not old artwork."""

import io

import numpy as np
from PIL import Image
import pymupdf as fitz
import pytest

from pdf_minify.core import pipeline
from pdf_minify.core.native_layer import NativeContext
from tools import bench_image_streams as images


def tagged_source(path, *, image_only=False, pages=1):
    data = io.BytesIO()
    y, x = np.indices((24, 24))
    Image.fromarray(np.where(((x+y) % 3)[:, :, None],
                            np.array([20, 80, 210], dtype=np.uint8),
                            np.array([250, 210, 90], dtype=np.uint8))).save(data, "PNG")
    with fitz.open() as doc, fitz.open() as stamp:
        tile = stamp.new_page(width=72, height=72)
        tile.insert_image(fitz.Rect(8, 8, 60, 45), stream=data.getvalue())
        if not image_only:
            tile.insert_text((8, 60), "Native figure", fontsize=8)
        for pno in range(pages):
            page = doc.new_page(width=120, height=120)
            root = page.show_pdf_page(fitz.Rect(20, 20, 92, 92), stamp)
            page.insert_text((8, 110), f"Page {pno+1}", fontsize=8)
            text = page.get_contents()[-1]
            doc.update_stream(text, b"/P <</MCID 0>> BDC\n" + doc.xref_stream(text) + b"\nEMC")
        page = doc[0]
        doc.update_stream(root, b"/Figure <</MCID 0>> BDC\n" + doc.xref_stream(root) + b"\nEMC")
        doc.xref_set_key(root, "StructParents", "1")
        doc.xref_set_key(page.xref, "StructParents", "0")
        tree, paragraph, figure, parents = [doc.get_new_xref() for _ in range(4)]
        doc.update_object(tree, f"<< /Type /StructTreeRoot /K [{paragraph} 0 R {figure} 0 R] "
                          f"/ParentTree {parents} 0 R /ParentTreeNextKey 2 >>")
        doc.update_object(paragraph, f"<< /Type /StructElem /S /P /P {tree} 0 R "
                          f"/Pg {page.xref} 0 R /K 0 >>")
        doc.update_object(figure, f"<< /Type /StructElem /S /Figure /P {tree} 0 R "
                          f"/Pg {page.xref} 0 R /Alt (Map illustration) "
                          "/A << /O /Layout /BBox [20 28 92 100] >> "
                          f"/K << /Type /MCR /MCID 0 /Pg {page.xref} 0 R /Stm {root} 0 R >> >>")
        doc.update_object(parents, f"<< /Nums [0 [{paragraph} 0 R] 1 [{figure} 0 R]] >>")
        doc.xref_set_key(doc.pdf_catalog(), "StructTreeRoot", f"{tree} 0 R")
        doc.xref_set_key(doc.pdf_catalog(), "MarkInfo", "<< /Marked true >>")
        doc.xref_set_key(doc.pdf_catalog(), "Lang", "(en-US)")
        doc.set_metadata({"title": "Tagged image test", "author": "Example author"})
        doc.set_toc([[1, "Kept bookmark", 1]])
        doc.embfile_add("note.txt", b"Kept attachment")
        doc.save(path)


@pytest.mark.parametrize("mode", ["bw-flate", "indexed"])
@pytest.mark.parametrize("image_only", [False, True])
def test_tagged_native_owners_and_document_semantics_are_retained(tmp_path, mode, image_only):
    source, target = tmp_path / "source.pdf", tmp_path / "result.pdf"
    tagged_source(source, image_only=image_only)
    original_bytes = source.read_bytes()
    pipeline.save_with_spec(str(source), str(target), dict(mode=mode, dpi=72, dpi_cap=72, colors=5))
    with fitz.open(source) as original, fitz.open(target) as saved:
        assert saved.metadata == original.metadata
        assert saved.get_toc() == original.get_toc()
        assert saved.embfile_get("note.txt") == b"Kept attachment"
        assert saved.xref_get_key(saved.pdf_catalog(), "MarkInfo/Marked")[1] == "true"
        assert saved.xref_get_key(saved.pdf_catalog(), "Lang")[1] == "en-US"
        tree = int(saved.xref_get_key(saved.pdf_catalog(), "StructTreeRoot")[1].split()[0])
        native = fitz.mupdf.pdf_document_from_fz_document(saved.this)
        root = fitz.mupdf.pdf_load_object(native, tree)
        kids = fitz.mupdf.pdf_dict_gets(root, "K")
        paragraph = fitz.mupdf.pdf_array_get(kids, 0)
        figure = fitz.mupdf.pdf_array_get(kids, 1)
        assert fitz.mupdf.pdf_to_int(fitz.mupdf.pdf_dict_gets(paragraph, "K")) == 0
        assert saved.xref_get_key(saved[0].xref, "StructParents")[1] == "0"
        assert fitz.mupdf.pdf_to_text_string(fitz.mupdf.pdf_dict_gets(figure, "Alt")) == "Map illustration"
        mcr = fitz.mupdf.pdf_dict_gets(figure, "K")
        form = fitz.mupdf.pdf_to_num(fitz.mupdf.pdf_dict_gets(mcr, "Stm"))
        assert form in {entry[0] for entry in saved[0].get_xobjects()}
        assert saved.xref_get_key(form, "StructParents")[1] == "1"
        assert b"/MCID 0" in saved.xref_stream(form)
        assert b"/MCID 0" in saved[0].read_contents()
        assert b"/Artifact BMC" in saved[0].read_contents()
        parent_tree = fitz.mupdf.pdf_dict_gets(root, "ParentTree")
        nums = fitz.mupdf.pdf_dict_gets(parent_tree, "Nums")
        for offset, element in ((1, paragraph), (3, figure)):
            assert fitz.mupdf.pdf_to_num(fitz.mupdf.pdf_array_get(
                fitz.mupdf.pdf_array_get(nums, offset), 0)) == fitz.mupdf.pdf_to_num(element)
        images.assert_native_text(original[0], saved[0])
        images.assert_no_retained_source_images(original, saved)
        all_images = [xref for xref in range(1, saved.xref_length())
                      if saved.xref_get_key(xref, "Subtype")[1] == "/Image"]
        assert all_images == [saved[0].get_images()[0][0]]
    assert source.read_bytes() == original_bytes


@pytest.mark.parametrize("mode", ["bw-flate", "indexed"])
def test_shared_forms_read_later_canvases_from_immutable_original(tmp_path, mode):
    source, target = tmp_path / "shared.pdf", tmp_path / "result.pdf"
    tagged_source(source, pages=2)
    pipeline.save_with_spec(str(source), str(target), dict(mode=mode, dpi=72, dpi_cap=72, colors=5))
    with fitz.open(source) as original, fitz.open(target) as saved:
        assert len(saved[0].get_image_info()) == len(saved[1].get_image_info()) == 1
        first, second = [page.get_images()[0][0] for page in saved]
        assert saved.xref_stream(first) == saved.xref_stream(second)
        for before, after in zip(original, saved):
            images.assert_native_text(before, after)
        images.assert_no_retained_source_images(original, saved)


def test_whole_file_gate_rejects_stale_tag_references_despite_one_page_image(tmp_path):
    source, target = tmp_path / "source.pdf", tmp_path / "bad.pdf"
    tagged_source(source)
    with fitz.open(source) as saved:
        page = saved[0]
        empty = saved.get_new_xref()
        saved.update_object(empty, "<<>>")
        saved.update_stream(empty, b"")
        page.set_contents(empty)
        saved.xref_set_key(page.xref, "Resources", "<<>>")
        stream = io.BytesIO()
        Image.new("RGB", (120, 120), "white").save(stream, "PNG")
        page.insert_image(page.rect, stream=stream.getvalue())
        saved.save(target, garbage=4)
    with fitz.open(source) as original, fitz.open(target) as saved:
        assert len(saved[0].get_images()) == 1
        with pytest.raises(AssertionError, match="retained replaced source image"):
            images.assert_no_retained_source_images(original, saved)


@pytest.mark.parametrize("tagged", [False, True])
def test_form_derivatives_reuse_identity_or_reject_incompatible_tag_scopes(tagged):
    m = fitz.mupdf
    with fitz.open() as doc:
        doc.new_page()
        xref = doc.get_new_xref()
        doc.update_object(xref, "<< /Type /XObject /Subtype /Form /BBox [0 0 10 10] "
                          + ("/StructParents 0 " if tagged else "") + "/Resources <<>> >>")
        doc.update_stream(xref, b"q Q")
        context = NativeContext(doc)
        resources = m.pdf_new_dict(context.native, 0)
        assert context.derivative(xref, b"first", resources) == xref
        assert context.derivative(xref, b"first", resources) == xref
        if tagged:
            with pytest.raises(ValueError, match="accessibility parent mapping"):
                context.derivative(xref, b"different", resources)
        else:
            clone = context.derivative(xref, b"different", resources)
            assert clone != xref
            assert doc.xref_stream(xref) == b"first"
            assert doc.xref_stream(clone) == b"different"
