"""Measured Zopfli/Brotli selection for prepared PDFs (§§255/256).

Only lossless storage changes: native resources and general-compressed image
samples participate; specialized J* payloads stay intact. §260 adds joint
image-predictor selection; frozen studies can explicitly request preservation.
The caller owns image processing/font subsetting and supplies the shared final
writer. Both encoders run once per distinct input, not once per trial PDF.
"""

from dataclasses import dataclass, replace
import errno
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import time
import uuid

import pymupdf as fitz

from .cancel import CancelToken
from .pdf_io import FITZ_LOCK
from . import stream_compression as streams
from .predictors import image_layout, predict_rows

_GENERAL_IMAGE_FILTERS = ("null", "/FlateDecode", "/BrotliDecode")


def _protected_xrefs(doc):
    """Specialized image bytes, including JBIG2's optional shared dictionary."""
    excluded = set()
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    for xref in range(1, doc.xref_length()):
        if not doc.xref_is_stream(xref) or doc.xref_get_key(xref, "Subtype")[1] != "/Image":
            continue
        filtr = doc.xref_get_key(xref, "Filter")[1]
        if filtr not in _GENERAL_IMAGE_FILTERS:
            excluded.add(xref)
        if "/JBIG2Decode" in filtr:
            parms = m.pdf_dict_gets(m.pdf_load_object(native, xref), "DecodeParms")
            entries = ([m.pdf_array_get(parms, i) for i in range(m.pdf_array_len(parms))]
                       if m.pdf_is_array(parms) else [parms])
            for entry in entries:
                shared = m.pdf_dict_gets(entry, "JBIG2Globals")
                if m.pdf_is_indirect(shared):
                    excluded.add(m.pdf_to_num(shared))
    return excluded


@dataclass(frozen=True)
class _Encoded:
    path: Path
    size: int
    filtr: str | None
    policy: str = ""
    decode_parms: str = "null"
    prediction: str = "preserve"
    uses_prediction: bool = False

    @property
    def cost(self):
        return (_stored_cost(self.size, self.filtr)
                + (len("/DecodeParms") + len(self.decode_parms) if self.decode_parms != "null" else 0))


@dataclass(frozen=True)
class _Pair:
    xref: int
    decode_parms: str
    decoded_hash: bytes
    zopfli: _Encoded
    brotli: _Encoded
    image: bool
    alternatives: tuple = ()
    predictable: bool = False

    def choice(self, brotli):
        return self.brotli if brotli else self.zopfli


def _eligible_xrefs(doc):
    """Production converts source imagery BEFORE this storage-only stage."""
    native = set(streams.native_stream_xrefs(doc)) - _protected_xrefs(doc)
    for xref in range(1, doc.xref_length()):
        if xref in native:
            yield xref, False
        elif (doc.xref_is_stream(xref)
              and doc.xref_get_key(xref, "Subtype")[1] == "/Image"
              and doc.xref_get_key(xref, "Filter")[1]
              in _GENERAL_IMAGE_FILTERS):
            yield xref, True


def _read(doc, xref):
    before = fitz.TOOLS.mupdf_warnings(reset=False)
    data = doc.xref_stream(xref)
    if data is None or fitz.TOOLS.mupdf_warnings(reset=False) != before:
        raise RuntimeError(f"Stream {xref} failed exact decoding for Best.")
    return data


def _install(doc, pair, choice):
    if isinstance(choice, bool):
        choice = pair.choice(choice)
    doc.update_stream(pair.xref, choice.path.read_bytes(), compress=False)
    doc.xref_set_key(pair.xref, "Filter", choice.filtr or "null")
    doc.xref_set_key(pair.xref, "DecodeParms", choice.decode_parms)


def _stored_cost(size, filtr):
    """Differing payload, decoder-name and /Length-digit bytes; rest is common."""
    return size + len(filtr or "null") + len(str(size))


def _encode_pairs(doc, directory, token, image_prediction="preserve", policies=("zopfli", "brotli")):
    cache = {}
    pairs = []
    raw_total = 0
    for xref, image in _eligible_xrefs(doc):
        streams.check_cancel(token)
        decoded = _read(doc, xref)
        digest = hashlib.sha256(decoded).digest()
        # xref_stream applies prediction too. Remove only the decoding
        # parameters temporarily to obtain the exact existing predicted bytes
        # for the preservation control. New OFF/ON variants use decoded rows.
        parms = doc.xref_get_key(xref, "DecodeParms")[1] if image else "null"
        predictor = doc.xref_get_key(xref, "DecodeParms/Predictor") if image else ("null", "null")
        was_predicted = predictor[0] == "int" and int(predictor[1]) > 1
        if image and parms != "null":
            doc.xref_set_key(xref, "DecodeParms", "null")
            try:
                data = _read(doc, xref)
            finally:
                doc.xref_set_key(xref, "DecodeParms", parms)
        else:
            data = decoded
        # Do not retain every page's decoded pixels. A digest indexes disk
        # artifacts; byte-for-byte per-stream readback below still guards
        # reuse, so even a cache-key collision cannot publish different data.
        variants = [("preserve", data, parms)]
        layout = image_layout(doc, xref, len(decoded)) if image and image_prediction != "preserve" else None
        if image and image_prediction == "off":
            variants = [("off", decoded, "null")]
        if image and image_prediction == "on" and layout is None:
            raise RuntimeError(f"Image stream {xref} has no supported PNG predictor layout.")
        if layout:
            width, height, bpc, colors = layout
            variants = []
            if image_prediction in ("off", "best"):
                variants.append(("off", decoded, "null"))
            if image_prediction in ("on", "best"):
                predicted_rows = predict_rows(decoded, width, height, bpc, colors, token)
                prediction_parms = (f"<< /Predictor 15 /Colors {colors} "
                                    f"/BitsPerComponent {bpc} /Columns {width} >>")
                variants.append(("on", predicted_rows, prediction_parms))
            if image_prediction == "best" and parms != "null":
                variants.append(("preserve", data, parms))
        alternatives = []
        for prediction, raw, decode_parms in variants:
            for policy in policies:
                streams.check_cancel(token)
                key = policy if raw else "empty", len(raw), hashlib.sha256(raw).digest()
                if key not in cache:
                    encoded, filtr = streams.encode_stream(raw, policy, directory=directory, token=token)
                    path = Path(directory) / f"stream-{len(cache)}-{policy}.bin"
                    path.write_bytes(encoded)
                    cache[key] = _Encoded(path, len(encoded), filtr, policy)
                encoded = cache[key]
                uses_prediction = prediction == "on" or (prediction == "preserve" and was_predicted)
                if decode_parms != "null" or prediction != "preserve" or encoded.policy != policy:
                    encoded = replace(encoded, policy=policy, decode_parms=decode_parms,
                                      prediction=prediction, uses_prediction=uses_prediction)
                alternatives.append(encoded)
        smallest = lambda policy: min((a for a in alternatives if a.policy == policy),
                                       key=lambda a: (a.cost, a.uses_prediction))
        zopfli = smallest("zopfli")
        brotli = smallest("brotli") if "brotli" in policies else zopfli
        pair = _Pair(xref, parms, digest, zopfli, brotli, image, tuple(alternatives), bool(layout))
        for choice in alternatives:
            streams.check_cancel(token)
            _install(doc, pair, choice)
            if _read(doc, xref) != decoded:
                raise RuntimeError(f"Stream {xref} failed exact Best readback.")
        pairs.append(pair)
        raw_total += len(data)
    return pairs, raw_total


def _assignments(pairs, policies):
    """Measure whole-file controls as well as locally cheapest assignments."""
    for policy in policies:
        choice = lambda pair: pair.choice(policy == "brotli")
        yield policy, tuple(choice(pair) for pair in pairs)
        if any(pair.predictable and len({a.prediction for a in pair.alternatives}) > 1 for pair in pairs):
            for prediction in ("off", "on", "preserve"):
                if not any(a.prediction == prediction for pair in pairs if pair.image for a in pair.alternatives):
                    continue
                assignment = tuple(next((a for a in pair.alternatives
                                         if a.policy == policy and a.prediction == prediction), choice(pair))
                                   for pair in pairs)
                yield f"{policy}-{prediction}", assignment
    yield "mixed", tuple(min(pair.alternatives,
                             key=lambda a: (a.cost, a.filtr == "/BrotliDecode", a.uses_prediction))
                         for pair in pairs)


def _stable_ids(doc, no_new_id):
    """Generate a changed-document ID ONCE, preserving the permanent first ID."""
    if no_new_id:
        return
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    ids = m.pdf_dict_gets(m.pdf_trailer(native), "ID")
    first = m.pdf_array_get(ids, 0)
    if m.pdf_is_string(first):
        # Use PDF syntax, not xref_get_key's decoded Unicode representation:
        # identifiers are binary strings and can contain NULs/escaped bytes.
        first_syntax = m.pdf_sprint_obj(None, 0, first, True, True)[0]
    else:
        first_syntax = f"<{uuid.uuid4().hex}>"
    doc.xref_set_key(-1, "ID", f"[{first_syntax} <{uuid.uuid4().hex}>]")


def _uses_brotli(doc):
    return any(doc.xref_is_stream(xref)
               and "/BrotliDecode" in doc.xref_get_key(xref, "Filter")[1]
               for xref in range(1, doc.xref_length()))


def _protected_signature(doc):
    return {(doc.xref_get_key(xref, "Filter")[1], hashlib.sha256(doc.xref_stream_raw(xref)).digest())
            for xref in _protected_xrefs(doc) if doc.xref_is_stream(xref)}


def _verify_saved(path, pairs, protected):
    """The shared writer must preserve decoded data and every J* payload too."""
    with fitz.open(path) as stored:
        actual = {(image, hashlib.sha256(_read(stored, xref)).digest())
                  for xref, image in _eligible_xrefs(stored)}
        expected = {(pair.image, pair.decoded_hash) for pair in pairs}
        if actual != expected or _protected_signature(stored) != protected:
            raise RuntimeError("Best candidate failed exact saved-file stream readback.")


def _publish(candidate, target, token):
    """Do not expose partial output or replace an existing result on cancellation."""
    streams.check_cancel(token)
    try:
        os.replace(candidate, target)
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
        # CLI callers can export across filesystems. An adjacent staging file
        # makes the final replace atomic there too; GUI paths share one workdir.
        descriptor, staging = tempfile.mkstemp(prefix=".pdf-minify-best-", suffix=".pdf",
                                               dir=Path(target).parent)
        os.close(descriptor)
        try:
            shutil.copyfile(candidate, staging)
            streams.check_cancel(token)
            os.replace(staging, target)
        finally:
            Path(staging).unlink(missing_ok=True)


def save_best_streams(doc, target, *, writer, directory=None, token=None,
                      brotli_declaration=False, no_new_id=False,
                      image_prediction="best", policy="best"):
    """Save the smallest actual homogeneous/mixed candidate, not a size estimate.

    This is best among evaluated assignments, not an exhaustive search of all
    possible stream combinations. Fewer Brotli streams, then fewer predicted
    streams, break exact file ties.
    """
    token = token or CancelToken()
    if policy not in ("best", "zopfli") or image_prediction not in ("off", "on", "best", "preserve"):
        raise ValueError("Unknown lossless encoder/predictor selection")
    policies = ("zopfli", "brotli") if policy == "best" else ("zopfli",)
    streams.check_cancel(token)
    started = time.perf_counter()
    with FITZ_LOCK, tempfile.TemporaryDirectory(prefix="best-streams-", dir=directory) as scratch:
        # A plain-container snapshot avoids B113 (editing IDs on an old xref
        # stream edits the object, not the writer's trailer). No pixels, fonts,
        # content or encoded images are processed again.
        snapshot = doc.tobytes(garbage=4, deflate=False, use_objstms=False, no_new_id=True)
        with fitz.open(stream=snapshot, filetype="pdf") as probe:
            _stable_ids(probe, no_new_id)
            snapshot = probe.tobytes(deflate=False, use_objstms=False, no_new_id=True)
            protected = _protected_signature(probe)
            pairs, raw_total = _encode_pairs(probe, scratch, token, image_prediction, policies)
        measured = []
        seen = set()
        for name, assignment in _assignments(pairs, policies):
            identity = tuple((a.path, a.filtr, a.decode_parms) for a in assignment)
            if identity in seen:
                continue
            seen.add(identity)
            streams.check_cancel(token)
            path = Path(scratch) / f"{name}.pdf"
            with fitz.open(stream=snapshot, filetype="pdf") as candidate:
                for pair, choice in zip(pairs, assignment):
                    _install(candidate, pair, choice)
                streams.set_brotli_declaration(candidate,
                                               brotli_declaration and _uses_brotli(candidate))
                writer(candidate, str(path), no_new_id=True)
            streams.check_cancel(token)
            _verify_saved(path, pairs, protected)
            measured.append((path.stat().st_size,
                             sum(a.filtr == "/BrotliDecode" for a in assignment),
                             sum(a.uses_prediction for a in assignment), name, path, assignment))
        size, brotli_count, prediction_count, name, path, assignment = min(measured, key=lambda row: row[:4])
        stats = dict(streams=len(pairs), image_streams=sum(pair.image for pair in pairs),
                     raw_bytes=raw_total,
                     encoded_bytes=sum(choice.size for choice in assignment),
                     brotli_streams=brotli_count, winner=name, file_bytes=size,
                     predictable_images=sum(pair.predictable for pair in pairs),
                     predicted_streams=prediction_count,
                     png_prediction_on_streams=sum(a.prediction == "on" for a in assignment),
                     candidate_bytes={row[3]: row[0] for row in measured})
        _publish(path, target, token)
    stats["encode_seconds"] = time.perf_counter() - started
    return stats
