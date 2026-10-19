"""LOSSY-02: real q75/q75 comparison with study-based JPX mapping (§267).

Equal slider values are the approved working visual-quality baseline.
No timing/CSV, synthetic size estimates or prerequisite quality calibration.
The observer records production inputs/results; it never changes encoding.
"""

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import __version__ as pillow_version, features
import pymupdf as fitz

from pdf_minify.core import pipeline, quality, stream_compression
from tools import bench_compression_overview as overview


DOCUMENTS = overview.DOCUMENTS
QUALITY = 75
DPI = 300
MODES = ("color", "jpx")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def recipe(mode, force):
    if mode not in MODES or type(force) is not bool:
        raise ValueError("Expected a lossy JPEG/JPEG2000 recipe and boolean FFPR")
    field = "jpeg_q" if mode == "color" else "jpx_q"
    return dict(mode=mode, dpi_cap=DPI, **{field: QUALITY}, force_raster=force,
                stream_compression="best", brotli_declaration=False)


def identity(documents):
    return dict(study="LOSSY-02-q75-jpeg-reference-v1", dpi=DPI, quality=QUALITY,
                visual_quality_basis="designer-study-ratio-matched-working-baseline",
                documents=[dict(asdict(d), source_sha256=file_digest(d.source)) for d in documents],
                environment=overview.study.environment(),
                benchmark_sha256=file_digest(__file__), pillow=pillow_version,
                libjpeg_turbo=features.version_feature("libjpeg_turbo"),
                openjpeg=features.version_codec("jpg_2000"),
                jpeg_profile=quality.JPEG_ENCODING_PROFILE,
                jpx_profile=quality.JPX_ENCODING_PROFILE,
                jpx_quality_mapping=quality.JPX_QUALITY_MAPPING)


def readback(path):
    """Validate every actual embedded frame and render every page at 72/300 DPI."""
    fitz.TOOLS.mupdf_warnings()
    with fitz.open(path) as doc:
        pages = [overview.study.images.page_signature(page, DPI) for page in doc]
        embedded = []
        for page in doc:
            for info in page.get_images(full=True):
                xref = info[0]
                # Image aliases may be shared by the writer across pages.
                # Counting references, rather than unique objects, preserves
                # correspondence to independently observed page canvases.
                embedded.append(dict(width=info[2], height=info[3],
                                     filter=doc.xref_get_key(xref, "Filter")[1],
                                     payload_sha256=digest(doc.xref_stream_raw(xref))))
        native = sorted(Counter(digest(doc.xref_stream(xref)) for xref in
                                stream_compression.native_stream_xrefs(doc)).items())
        # Normalize tuples at creation, not only after checkpoint reload.
        return json.loads(json.dumps(dict(
            pages=pages, images=embedded, native=native,
            warnings=fitz.TOOLS.mupdf_warnings(),
            brotli_declaration=stream_compression.brotli_declaration_present(doc))))


def verify_record(record, *, rerender=True):
    path = Path(record["pdf"])
    if (not path.is_file() or path.stat().st_size != record["complete_pdf_bytes"]
            or file_digest(path) != record["pdf_sha256"]):
        raise ValueError(f"Changed measured lossy PDF: {path}")
    if record["recipe"] != recipe(record["mode"], record["force_raster"]):
        raise ValueError("Changed lossy recipe")
    expected_filter = "/DCTDecode" if record["mode"] == "color" else "/JPXDecode"
    canvases, images = record["canvases"], record["readback"]["images"]
    observed = [dict(width=c["width"], height=c["height"], filter=c["filter"],
                     payload_sha256=c["payload_sha256"]) for c in canvases]
    if images != observed or any(c["filter"] != expected_filter for c in canvases):
        raise ValueError("Saved codec/payload differs from the actual production encoder")
    for canvas in canvases:
        reference = canvas["quality_reference"]
        raw = canvas["width"] * canvas["height"] * 3
        if (reference["quality"] != QUALITY or reference["raw_sample_bytes"] != raw
                or type(reference["jpeg_bytes"]) is not int or reference["jpeg_bytes"] <= 0
                or reference["jpeg_ratio"] != raw / reference["jpeg_bytes"]
                or reference["jpx_target_rate"] != quality.jpx_reference_rate(raw, reference["jpeg_bytes"])
                or len(reference["jpeg_sha256"]) != 64):
            raise ValueError("Changed or invalid measured quality reference")
        if record["mode"] == "color" and reference["jpeg_sha256"] != canvas["payload_sha256"]:
            raise ValueError("JPEG reference is not the actual JPEG payload")
    if record["readback"]["brotli_declaration"]:
        raise ValueError("Unexpected compatibility declaration")
    if rerender and record["readback"] != readback(path):
        raise ValueError("Changed all-page rendering or saved PDF structure")


def verify_pair(left, right):
    if (left["document"] != right["document"] or left["force_raster"] != right["force_raster"]
            or (left["mode"], right["mode"]) != MODES or left["pdf"] == right["pdf"]):
        raise ValueError("Mismatched or aliased lossy comparison pair")
    samples = lambda row: [{k: c[k] for k in ("width", "height", "samples_sha256")}
                          for c in row["canvases"]]
    if samples(left) != samples(right):
        raise ValueError("JPEG/JPEG2000 received different prepared RGB samples")
    for jpeg, jpx in zip(left["canvases"], right["canvases"], strict=True):
        if (jpeg["quality_reference"] != jpx["quality_reference"]
                or jpeg["payload_sha256"] != jpx["quality_reference"]["jpeg_sha256"]):
            raise ValueError("JPX reference differs from the actual paired JPEG payload")
    # Lossy bitmap renders must differ; the supposedly fixed native side must not.
    left_pages = [{k: v for k, v in p.items() if k != "renders"} for p in left["readback"]["pages"]]
    right_pages = [{k: v for k, v in p.items() if k != "renders"} for p in right["readback"]["pages"]]
    if left_pages != right_pages or left["readback"]["native"] != right["readback"]["native"]:
        raise ValueError("Lossy comparison changed native content or page geometry")


def measure(document, force, mode, folder, current_identity, *, resume=False):
    folder.mkdir(parents=True, exist_ok=resume)
    checkpoint, output = folder / "metrics.json", folder / "filtered.pdf"
    spec = recipe(mode, force)
    job = dict(identity=current_identity, document=asdict(document), recipe=spec)
    if resume and checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous["job"] != job:
            raise ValueError("Changed lossy benchmark identity/input/recipe")
        verify_record(previous["result"])
        return previous["result"]
    if output.exists():
        raise FileExistsError(f"Unverified existing lossy output: {output}")
    observed = []
    encoder, jpeg_encoder = pipeline.color_canvas_payload, pipeline.jpeg_encode
    references = []

    def observe_jpeg(img, q=QUALITY):
        data = jpeg_encoder(img, q)
        raw = img.width * img.height * 3
        references.append(dict(quality=q, raw_sample_bytes=raw, jpeg_bytes=len(data),
                               jpeg_sha256=digest(data), jpeg_ratio=raw / len(data),
                               jpx_target_rate=quality.jpx_reference_rate(raw, len(data))))
        return data

    def observe(img, *args, **kwargs):
        samples = dict(width=img.width, height=img.height,
                       samples_sha256=digest(img.tobytes()))
        prior_count = len(references)
        payload = encoder(img, *args, **kwargs)
        if len(references) != prior_count + 1:
            raise ValueError("Expected one actual JPEG reference per prepared canvas")
        observed.append(dict(samples, filter=payload["filter"],
                             payload_sha256=digest(payload["stream"]),
                             quality_reference=references[-1]))
        return payload

    # Observation only: exact production helper, arguments and returned payload.
    with (patch.object(pipeline, "color_canvas_payload", observe),
          patch.object(pipeline, "jpeg_encode", observe_jpeg)):
        pipeline.save_with_spec(document.source, str(output), spec, workdir=str(folder))
    if file_digest(document.source) != next(d["source_sha256"] for d in current_identity["documents"]
                                             if d["key"] == document.key):
        raise ValueError("Source changed during lossy benchmark")
    if not force:
        with fitz.open(document.source) as original, fitz.open(output) as saved:
            if len(original) != len(saved):
                raise ValueError("Lossy benchmark changed page count")
            for before, after in zip(original, saved, strict=True):
                overview.study.images.assert_native_text(before, after)
    result = dict(document=document.key, mode=mode, force_raster=force, recipe=spec,
                  pdf=str(output), pdf_sha256=file_digest(output),
                  complete_pdf_bytes=output.stat().st_size, canvases=observed,
                  readback=readback(output))
    verify_record(result, rerender=False)  # the readback immediately above is fresh
    checkpoint.write_text(json.dumps(dict(job=job, result=result), indent=2) + "\n")
    print(json.dumps(dict(document=document.key, force_raster=force, mode=mode,
                          complete_pdf_bytes=result["complete_pdf_bytes"],
                          pages=len(result["readback"]["pages"]), canvases=len(observed))), flush=True)
    return result


def table(documents, records):
    index = {}
    for row in records:
        key = row["document"], row["force_raster"], row["mode"]
        if key in index:
            raise ValueError("Duplicate lossy measurement")
        size = row["complete_pdf_bytes"]
        if type(size) is not int or size <= 0:
            raise ValueError("Expected positive measured complete-file bytes")
        index[key] = row
    wanted = {(d.key, force, mode) for d in documents for force in (False, True) for mode in MODES}
    if set(index) != wanted:
        raise ValueError("Incomplete or unexpected lossy measurements")
    for document in documents:
        for force in (False, True):
            verify_pair(*(index[document.key, force, mode] for mode in MODES))
    lines = ["| Algorithm combination | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|" * len(documents)]
    for force in (False, True):
        for mode in MODES:
            label = ("Color FFPR + " if force else "") + ("JPEG q75" if mode == "color" else "JPEG2000 q75")
            cells = []
            for document in documents:
                size = index[document.key, force, mode]["complete_pdf_bytes"]
                minimum = min(index[document.key, force, m]["complete_pdf_bytes"] for m in MODES)
                cell = f"{size:,}"
                cells.append(f"**{cell}**" if size == minimum else cell)
            lines.append("| " + label + " | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def run(folder, documents=DOCUMENTS, *, resume=False):
    folder.mkdir(parents=True, exist_ok=resume)
    current = identity(documents)
    checkpoint = folder / "metrics.json"
    if resume and checkpoint.exists() and json.loads(checkpoint.read_text())["identity"] != current:
        raise ValueError("Changed lossy study scope or producing implementation")
    records = []
    # Get a useful artwork result first, without changing the six-column table.
    for document in sorted(documents, key=lambda d: (d.key != "art", d.key)):
        for force in (False, True):
            for mode in MODES:
                target = folder / document.key / ("ffpr" if force else "native") / mode
                record = measure(document, force, mode, target, current,
                                 resume=resume and target.exists())
                records.append(record)
                checkpoint.write_text(json.dumps(dict(identity=current, records=records, complete=False),
                                                 indent=2) + "\n")
            verify_pair(records[-2], records[-1])
    markdown = table(documents, records)
    (folder / "table.md").write_text(markdown)
    checkpoint.write_text(json.dumps(dict(identity=current, records=records, complete=True), indent=2) + "\n")
    print(markdown, flush=True)
    print(f"LOSSY-02 COMPLETE: {len(records)} verified complete PDFs", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args.output, resume=args.resume)


if __name__ == "__main__":
    main()
