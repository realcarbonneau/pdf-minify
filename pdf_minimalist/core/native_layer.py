"""Keep original native operators; remove only replaced bitmap/backdrop paint.

MuPDF's sanitizer can defer text state across a Form call (B111). It is not
a safe way to preserve native artwork. Token edits here leave text, graphics
state, clipping and native opacity resources untouched. MuPDF parses PDF
strings/objects and consumes inline images through its actual image decoder.
"""

import pymupdf as fitz

from .pdf_io import CancelledError

m = fitz.mupdf
_PAINT = {"S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"}
_FILL_REMOVED = {"f": b" n ", "F": b" n ", "f*": b" n ",
                 "B": b" S ", "B*": b" S ", "b": b" s ", "b*": b" s "}


def _inline_end(stream, lexer, native, resources):
    """Consume binary samples via the decoder, never search samples for EI."""
    properties = m.pdf_parse_dict(native, stream, lexer)
    ch = m.fz_read_byte(stream)  # required whitespace following ID
    if ch == 13 and m.fz_peek_byte(stream) == 10:
        m.fz_read_byte(stream)
    processor = m.PdfProcessor2()
    m.pdf_processor_push_resources(processor, resources)
    try:
        stack = m.PdfResourceStack(processor.m_internal.rstack)
        image = m.pdf_load_inline_image(native, stack, properties, stream)
        # Keep the decoded image alive until the decoder has consumed input.
        if not image:
            raise RuntimeError("Cannot decode inline image boundary")
        kind = m.pdf_lex(stream, lexer)
        if kind != m.PDF_TOK_KEYWORD or lexer.m_internal.scratch != "EI":
            raise RuntimeError("Missing inline image terminator after decoded samples")
        return m.fz_tell(stream)
    finally:
        m.pdf_close_processor(processor)


class NativeContext:
    """One document's immutable Form inputs and identity-preserving derivatives.

    MCR /Stm references and StructParents describe the original Form owners.
    Keep the first derivative in that owner, and reuse identical derivatives.
    Untagged Forms can have context-specific copies. A tagged Form cannot be
    split without retagging its parent mapping, so reject that case honestly.
    """
    def __init__(self, doc):
        self.doc = doc
        self.native = m.pdf_document_from_fz_document(doc.this)
        self.originals = {}
        self.variants = {}

    def original(self, xref):
        if xref not in self.originals:
            owner = m.pdf_load_object(self.native, xref)
            self.originals[xref] = (
                self.doc.xref_object(xref), self.doc.xref_stream(xref),
                m.pdf_dict_get(owner, m.PDF_ENUM_NAME_Resources),
                m.pdf_is_int(m.pdf_dict_gets(owner, "StructParents")))
        return self.originals[xref]

    def derivative(self, xref, content, resources):
        original, _, _, tagged = self.original(xref)
        serialized, _ = m.pdf_sprint_obj(None, 0, resources, 1, 1)
        signature = (content, serialized)
        variants = self.variants.setdefault(xref, {})
        if signature in variants:
            return variants[signature]
        if variants and tagged:
            raise ValueError("Tagged native Form requires incompatible derivatives; "
                             "cannot preserve its accessibility parent mapping")
        target = self.doc.get_new_xref() if variants else xref
        self.doc.update_object(target, original)
        self.doc.update_stream(target, content)
        m.pdf_dict_put(m.pdf_load_object(self.native, target),
                       m.PDF_ENUM_NAME_Resources, resources)
        variants[signature] = target
        return target


class _Foreground:
    def __init__(self, page, token, backdrops, context):
        self.doc, self.token = page.parent, token
        if context.doc is not self.doc:
            raise ValueError("Native context belongs to another document")
        self.context = context
        self.native = m.pdf_document_from_fz_document(self.doc.this)
        self.to_page = page.transformation_matrix
        self.backdrops = backdrops

    def rewrite(self, data, resources, matrix, opacity=1, ancestors=()):
        if len(ancestors) > 64:
            raise RuntimeError("Native Form nesting exceeds safety limit")
        result_resources = m.pdf_copy_dict(resources)
        xobjects = m.pdf_dict_get(resources, m.PDF_ENUM_NAME_XObject)
        # Start without bitmap/unused Form entries. Invoked native Forms are
        # copied below; opacity masks and Type 3 font resources are untouched.
        result_xobjects = m.pdf_new_dict(self.native, 4)
        m.pdf_dict_put(result_resources, m.PDF_ENUM_NAME_XObject, result_xobjects)
        stream = m.fz_open_buffer(m.fz_new_buffer_from_copied_data(data))
        lexer = m.PdfLexbuf(256)
        operands, edits, states = [], [], []
        rectangle, segments, kept = None, 0, 0
        while True:
            if self.token.cancelled:
                raise CancelledError()
            start = m.fz_tell(stream)
            kind = m.pdf_lex(stream, lexer)
            if kind == m.PDF_TOK_EOF:
                break
            value = None
            if kind == m.PDF_TOK_OPEN_DICT:
                m.pdf_parse_dict(self.native, stream, lexer)
            elif kind == m.PDF_TOK_OPEN_ARRAY:
                m.pdf_parse_array(self.native, stream, lexer)
            elif kind == m.PDF_TOK_NAME:
                value = lexer.m_internal.scratch
            elif kind == m.PDF_TOK_INT:
                value = lexer.m_internal.i
            elif kind == m.PDF_TOK_REAL:
                value = lexer.m_internal.f
            end = m.fz_tell(stream)
            if kind != m.PDF_TOK_KEYWORD:
                operands.append((start, end, value))
                continue
            operator = lexer.m_internal.scratch
            values = [operand[2] for operand in operands]
            if operator == "q":
                states.append((fitz.Matrix(matrix), opacity))
            elif operator == "Q" and states:
                matrix, opacity = states.pop()
            elif operator == "cm":
                matrix = fitz.Matrix(*values) * matrix
            elif operator == "gs":
                state = m.pdf_dict_gets(m.pdf_dict_get(resources, m.PDF_ENUM_NAME_ExtGState), values[0])
                ca = m.pdf_dict_get(state, m.PDF_ENUM_NAME_ca)
                if m.pdf_is_number(ca):
                    opacity = m.pdf_to_real(ca)
            elif operator == "re":
                x, y, w, h = values
                rectangle = fitz.Rect(x, y, x + w, y + h) * matrix * self.to_page
                segments += 1
            elif operator in ("m", "l", "c", "v", "y"):
                segments += 1
            elif operator in _PAINT:
                backdrop = (segments == 1 and rectangle is not None and opacity == 1
                            and any(max(abs(a-b) for a, b in zip(rectangle, rect)) < .01
                                    for rect in self.backdrops))
                if backdrop and operator in _FILL_REMOVED:
                    # Preserve a simultaneous native stroke and any pending
                    # clipping path, rather than deleting the entire path.
                    edits.append((start, end, _FILL_REMOVED[operator]))
                    kept += operator in ("B", "B*", "b", "b*")
                elif operator != "n":
                    kept += 1
                rectangle, segments = None, 0
            elif operator == "BI":
                edits.append((start, _inline_end(stream, lexer, self.native, resources), b" "))
            elif operator == "Do":
                obj = m.pdf_dict_gets(xobjects, values[0])
                subtype = m.pdf_to_name(m.pdf_dict_get(obj, m.PDF_ENUM_NAME_Subtype))
                if subtype == "Image":
                    edits.append((operands[0][0], end, b" "))
                elif subtype == "Form":
                    xref = m.pdf_to_num(obj)
                    if xref in ancestors:
                        raise RuntimeError("Cyclic native Form reference")
                    _, original_content, form_resources, tagged = self.context.original(xref)
                    if not form_resources:
                        form_resources = resources
                    form_matrix = m.pdf_dict_get(obj, m.PDF_ENUM_NAME_Matrix)
                    transform = fitz.Matrix(*(m.pdf_array_get_real(form_matrix, i) for i in range(6))) if form_matrix else fitz.Matrix(1, 1)
                    content, own_resources, count = self.rewrite(
                        original_content, form_resources, transform * matrix,
                        opacity, (*ancestors, xref))
                    if count or tagged:
                        target = self.context.derivative(xref, content, own_resources)
                        m.pdf_dict_puts(result_xobjects, values[0],
                                       m.pdf_new_indirect(self.native, target, 0))
                        # Keep MCID-bearing containers even when their original
                        # bitmap paint is now in the composite underlay.
                        kept += count or 1
                    else:
                        edits.append((operands[0][0], end, b" "))
                else:
                    # Unknown/legacy non-image XObjects are not raster paint
                    # that this policy authorizes deleting.
                    m.pdf_dict_puts(result_xobjects, values[0], obj)
                    kept += 1
            elif operator in ("Tj", "TJ", "'", '"', "sh"):
                kept += 1
            operands.clear()
        for start, end, replacement in sorted(edits, reverse=True):
            data = data[:start] + replacement + data[end:]
        return data, result_resources, kept


def retain_native_foreground(page, token, backdrops, *, context=None):
    """Remove replaced image paint while retaining original native semantics."""
    filter = _Foreground(page, token, backdrops, context or NativeContext(page.parent))
    owner = m.pdf_load_object(filter.native, page.xref)
    resources = m.pdf_dict_get_inheritable(owner, m.PDF_ENUM_NAME_Resources)
    content, resources, kept = filter.rewrite(page.read_contents(), resources, fitz.Matrix(1, 1))
    xref = page.parent.get_new_xref()
    page.parent.update_object(xref, "<<>>")
    page.parent.update_stream(xref, content)
    page.set_contents(xref)
    # set_contents can replace the page dictionary; don't mutate a detached
    # object loaded before that operation.
    owner = m.pdf_load_object(filter.native, page.xref)
    m.pdf_dict_put(owner, m.PDF_ENUM_NAME_Resources, resources)
    from .marked_content import repair_native_tags
    repair_native_tags(page, token)
    return kept
