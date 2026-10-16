"""Repair image-only whitespace tags orphaned by native-layer extraction.

MuPDF sanitizes drawing operators but can leave an ActualText whitespace tag
around a removed image and its surviving clipping/state operators (B109).
There is then no positioned content to which that replacement text applies.
Use MuPDF's PDF lexer/parser, not regexes over strings or binary PDF data.
Real text-bearing tags and non-whitespace replacement text are never removed.
"""

import pymupdf as fitz
from .pdf_io import CancelledError

m = fitz.mupdf


def repair_native_tags(page, token=None):
    doc = page.parent
    native = m.pdf_document_from_fz_document(doc.this)
    streams = [(xref, page.xref) for xref in page.get_contents()]
    streams += [(xref, xref) for xref, *_ in page.get_xobjects()]
    for xref, owner in dict.fromkeys(streams):
        data = doc.xref_stream(xref)
        if b"ActualText" not in data and b"BDC" not in data:
            continue
        obj = m.pdf_load_object(native, owner)
        resources = m.pdf_dict_get_inheritable(obj, m.PDF_ENUM_NAME_Resources)
        repaired = _repair_stream(data, native, resources, token)
        if repaired != data:
            doc.update_stream(xref, repaired)


def _repair_stream(data, native, resources, token=None):
    stream = m.fz_open_buffer(m.fz_new_buffer_from_copied_data(data))
    lexer = m.PdfLexbuf(256)
    operands, tags, edits = [], [], []
    while True:
        if token and token.cancelled:
            raise CancelledError()
        start = m.fz_tell(stream)
        kind = m.pdf_lex(stream, lexer)
        if kind == m.PDF_TOK_EOF:
            break
        value = None
        if kind == m.PDF_TOK_OPEN_DICT:
            value = m.pdf_parse_dict(native, stream, lexer)
        elif kind == m.PDF_TOK_OPEN_ARRAY:
            m.pdf_parse_array(native, stream, lexer)
        elif kind == m.PDF_TOK_NAME:
            value = lexer.m_internal.scratch
        end = m.fz_tell(stream)
        if kind != m.PDF_TOK_KEYWORD:
            operands.append((start, end, value))
            continue
        operator = lexer.m_internal.scratch
        if operator == "BDC":
            first, last, properties = operands[-1]
            if isinstance(properties, str):
                properties = m.pdf_dict_gets(m.pdf_dict_get(resources, m.PDF_ENUM_NAME_Properties), properties)
            actual = m.pdf_to_text_string(m.pdf_dict_get(properties, m.PDF_ENUM_NAME_ActualText)) if properties else ""
            tags.append(dict(start=first, end=last, properties=properties,
                             whitespace=bool(actual) and not actual.strip(), positioned=False))
        elif operator == "BMC":
            tags.append(None)
        elif operator == "EMC" and tags:
            tag = tags.pop()
            if tag and tag["whitespace"] and not tag["positioned"]:
                properties = m.pdf_copy_dict(tag["properties"])
                m.pdf_dict_del(properties, m.PDF_ENUM_NAME_ActualText)
                text, _ = m.pdf_sprint_obj(None, 0, properties, 1, 1)
                edits.append((tag["start"], tag["end"], b" " + text.encode("ascii") + b" "))
        elif operator in ("Tj", "TJ", "'", '"', "Do"):
            for tag in tags:
                if tag:
                    tag["positioned"] = True
        elif operator == "BI":
            # Native-layer extraction must have removed inline bitmap paint.
            # Never attempt to lex arbitrary binary inline samples as operators.
            raise RuntimeError("Native layer still contains an inline bitmap")
        operands.clear()
    for start, end, replacement in sorted(edits, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data
