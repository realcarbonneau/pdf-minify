"""Rerun every published Brotli encoding from verified prepared PDF samples.

No rasterization, palette fitting or thresholding. Every treatment is a new
complete save through the shared production optimizer; old evidence is immutable.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pymupdf as fitz

from tools import bench_integrated_compression as study

PUBLICATION = Path(".tmp/compression-experiments/publication-20261017/publication.json")
FFPR = Path(".tmp/compression-experiments/ffpr-brotli-zopfli-300dpi-20261017/metrics.json")
IMAGE = Path(".tmp/image-stream-compression/size-20261015/metrics.json")
NATIVE = Path(".tmp/native-stream-compression/main/metrics.json")
REUSABLE_PRODUCER = "262e681deba150b7b066a1e0eb2f640dff83de492b4016f5a941c87f644c9f75"
_ENCODER = study.streams._brotli
_CACHE = {}
_CACHE_BYTES = 0
_COUNTS = Counter()


def digest(data):
    return sha256(data).hexdigest()


def file_hash(path):
    hasher = sha256()
    with Path(path).open("rb") as source:
        while data := source.read(1024 * 1024):
            hasher.update(data)
    return hasher.hexdigest()


def cached_brotli(data, level):
    """Cache only fresh current-run encodings; there are no timing rankings."""
    global _CACHE_BYTES
    key = (level, digest(data))
    if key not in _CACHE:
        encoded = _ENCODER(data, level)
        if _CACHE_BYTES + len(encoded) > 256 * 1024 * 1024:
            _CACHE.clear()
            _CACHE_BYTES = 0
        _CACHE[key] = encoded
        _CACHE_BYTES += len(encoded)
        _COUNTS["fresh_encodes"] += 1
    else:
        _COUNTS["fresh_run_cache_hits"] += 1
    return _CACHE[key]


def rendered_graph(doc):
    """Canonical reachable PDF graph, independent of saved xref numbering.

    Includes geometry, native operators/fonts, images/masks/resources, semantic
    tags, links, metadata, attachments and trailer IDs. Native streams compare
    decoded bytes; images/other streams compare their exact encoded bytes.
    Length is derived from those bytes, not a separate rendering property.
    Container/xref streams are not part of the reachable document graph.
    """
    m = fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    seen = {}
    native_streams = set(study.streams.native_stream_xrefs(doc))

    def visit(obj, stream_xref=None):
        if m.pdf_is_indirect(obj):
            xref = m.pdf_to_num(obj)
            if xref in seen:
                return ["ref", seen[xref]]
            identifier = len(seen)
            seen[xref] = identifier
            return ["object", identifier, visit(m.pdf_resolve_indirect(obj),
                    xref if doc.xref_is_stream(xref) else None)]
        if m.pdf_is_dict(obj):
            items = {m.pdf_to_name(m.pdf_dict_get_key(obj, i)): m.pdf_dict_get_val(obj, i)
                     for i in range(m.pdf_dict_len(obj))}
            value = [[name, visit(items[name])] for name in sorted(items)
                     if stream_xref is None or name != "Length"]
            if stream_xref is not None:
                data = (doc.xref_stream(stream_xref) if stream_xref in native_streams
                        else doc.xref_stream_raw(stream_xref))
                return ["stream", value, digest(data)]
            return ["dict", value]
        if m.pdf_is_array(obj):
            return ["array", [visit(m.pdf_array_get(obj, i)) for i in range(m.pdf_array_len(obj))]]
        # MuPDF prints binary PDF strings losslessly (including embedded NULs).
        return ["value", m.pdf_sprint_obj(None, 0, obj, True, True)[0]]

    trailer = m.pdf_trailer(native)
    graph = [visit(m.pdf_dict_gets(trailer, key)) for key in ("Root", "Info", "ID", "Encrypt")]
    return digest(json.dumps(graph, separators=(",", ":"), ensure_ascii=True).encode())


def image_signature(doc):
    return sorted(Counter(digest(doc.xref_stream_raw(xref))
                         for xref in range(1, doc.xref_length())
                         if doc.xref_is_stream(xref) and
                         doc.xref_get_key(xref, "Subtype")[1] == "/Image").items())


def rerun_brotli_images(doc, directory):
    count = 0
    for xref in range(1, doc.xref_length()):
        if (not doc.xref_is_stream(xref) or doc.xref_get_key(xref, "Subtype")[1] != "/Image"
                or doc.xref_get_key(xref, "Filter")[1] != "/BrotliDecode"):
            continue
        packed = doc.xref_stream(xref)
        decode_params = doc.xref_get_key(xref, "DecodeParms")[1]
        raw = packed
        kind, predictor = doc.xref_get_key(xref, "DecodeParms/Predictor")
        if kind != "null":
            if predictor != "15":
                raise ValueError("Unknown Brotli image prediction; no silent substitution")
            width = int(doc.xref_get_key(xref, "Width")[1])
            height = int(doc.xref_get_key(xref, "Height")[1])
            bpc = int(doc.xref_get_key(xref, "BitsPerComponent")[1])
            if doc.xref_get_key(xref, "DecodeParms/Colors")[1] != "1":
                raise ValueError("Unexpected packed image components")
            raw = study.images.predict_rows(packed, width, height, bpc)
        payload, filtr = study.streams.encode_stream(raw, "brotli", directory=str(directory))
        doc.update_stream(xref, payload, compress=False)
        doc.xref_set_key(xref, "Filter", filtr)
        if decode_params != "null":
            doc.xref_set_key(xref, "DecodeParms", decode_params)
        if doc.xref_stream(xref) != packed:
            raise ValueError("Brotli image rerun changed prepared samples")
        count += 1
    return count


def normalize_old_declaration(doc, case):
    """Undo only the forced version marker whose old producer/source prove it.

    Native/image old benchmark writers explicitly set catalog /Version /2.0
    when adding this declaration. New FFPR pages have no original catalog;
    retained-native pages preserve their original source's catalog version.
    The source file header is never downgraded or edited as raw PDF bytes.
    """
    declared = study.streams.brotli_declaration_present(doc)
    before = doc.xref_get_key(doc.pdf_catalog(), "Version")[1]
    ffpr = (case.get("mode", "").endswith("-ffpr") or
            bool(case.get("recipe", {}).get("force_raster", False)))
    if ffpr:
        original_version = "null"
    else:
        with fitz.open(case["source"]) as source:
            original_version = source.xref_get_key(source.pdf_catalog(), "Version")[1]
    if declared and before == "/2.0":
        doc.xref_set_key(doc.pdf_catalog(), "Version", original_version)
    study.streams.set_brotli_declaration(doc, False)
    return dict(declared_before=declared, catalog_before=before,
                original_catalog_version=original_version,
                catalog_after=doc.xref_get_key(doc.pdf_catalog(), "Version")[1])


def import_verified(job, directory, identity, previous):
    """Bounded import of successful first-pass jobs, never its rejected outputs.

    The pinned producer differed only in adding null DecodeParms to plain
    images. Its successful exact-graph checks exclude all affected outputs.
    Repeat the graph/hash proof, not already successful Brotli encoding.
    """
    previous = Path(previous)
    checkpoint = previous / "jobs" / job["key"] / "metrics.json"
    if not checkpoint.exists():
        return None
    proof = json.loads(checkpoint.read_text())
    old_identity = proof["identity"]
    if (file_hash(previous / "implementation.py") != REUSABLE_PRODUCER or
            old_identity["implementation"] != REUSABLE_PRODUCER or proof["job"] != job or
            any(old_identity[k] != identity[k] for k in ("inputs", "environment", "jobs_sha256"))):
        raise ValueError("Incompatible verified-import producer")
    result = proof["result"]
    if (file_hash(result["pdf"]) != result["pdf_sha256"] or
            Path(result["pdf"]).stat().st_size != result["complete_pdf_bytes"]):
        raise ValueError("Changed verified-import PDF")
    with fitz.open(job["result"]["pdf"]) as original, fitz.open(result["pdf"]) as output:
        normalize_old_declaration(original, job["case"])
        if (rendered_graph(original) != rendered_graph(output) or
                image_signature(original) != image_signature(output) or
                study.streams.brotli_declaration_present(output)):
            raise ValueError("Changed verified-import document")
    directory.mkdir(parents=True)
    target = directory / "declaration-off.pdf"
    target.write_bytes(Path(result["pdf"]).read_bytes())
    evidence = dict(proof, identity=identity, result=dict(result, pdf=str(target)),
                    reused_verified=dict(checkpoint=str(checkpoint), sha256=file_hash(checkpoint)),
                    encoder=dict(fresh_encodes=0, fresh_run_cache_hits=0),
                    imported_encoder=proof["encoder"])
    (directory / "metrics.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(dict(completed=job["key"], bytes=result["complete_pdf_bytes"],
                          imported_verified=True)), flush=True)
    return evidence


def measure(job, directory, identity, resume=False, reuse_verified=None):
    directory = Path(directory)
    checkpoint = directory / "metrics.json"
    if resume and checkpoint.exists():
        prior = json.loads(checkpoint.read_text())
        if prior["identity"] != identity or prior["job"] != job:
            raise ValueError("Changed Brotli rerun identity")
        result = prior["result"]
        if (Path(result["pdf"]).stat().st_size != result["complete_pdf_bytes"] or
                file_hash(result["pdf"]) != result["pdf_sha256"]):
            raise ValueError("Changed rerun output")
        return prior
    old = job["result"]
    source = Path(old["pdf"])
    if source.stat().st_size != old["complete_pdf_bytes"] or file_hash(source) != old["pdf_sha256"]:
        raise ValueError(f"Changed original measured PDF: {source}")
    if file_hash(job["case"]["source"]) != job["case"]["input_sha256"]:
        raise ValueError("Changed original source")
    if reuse_verified:
        imported = import_verified(job, directory, identity, reuse_verified)
        if imported:
            return imported
    directory.mkdir(parents=True, exist_ok=resume)
    target = directory / "declaration-off.pdf"
    if target.exists():
        raise FileExistsError("Refusing an unowned partial output")
    prior_counts = dict(_COUNTS)
    previous_encoder = study.streams._brotli
    study.streams._brotli = cached_brotli
    work = study.pipeline._ENCODE_WORKDIR.set(str(directory))
    policy = study.pipeline._STREAM_POLICY.set(old["native_policy"])
    declaration = study.pipeline._BROTLI_DECLARATION.set(False)
    try:
        with fitz.open(source) as doc:
            old_images = image_signature(doc)
            metadata = normalize_old_declaration(doc, job["case"])
            graph = rendered_graph(doc)
            encoded_images = rerun_brotli_images(doc, directory)
            # No font subsetting or image transforms. The shared saver reruns
            # native encoding at the selected actual policy, including level 9.
            study.pipeline._save_optimized_pdf(doc, str(target), no_new_id=True, subset_fonts=False)
        with fitz.open(target) as doc:
            if study.streams.brotli_declaration_present(doc):
                raise ValueError("Declaration was not omitted")
            if rendered_graph(doc) != graph:
                raise ValueError("Rerun changed the rendered document graph")
            if image_signature(doc) != old_images:
                raise ValueError("Brotli image rerun changed fixed encoded image payloads")
            pages = len(doc)
        result = dict(old, pdf=str(target), pdf_sha256=file_hash(target),
                      complete_pdf_bytes=target.stat().st_size, brotli_declaration=False,
                      exact_native=True, exact_images=True, exact_all_page_pixels=True)
        evidence = dict(identity=identity, job=job, result=result, metadata=metadata,
                        pages=pages, rendered_graph_sha256=graph,
                        validation="unchanged rendered graph/streams; earlier all-page pixel evidence reused",
                        brotli_image_streams_rerun=encoded_images,
                        encoder={key: _COUNTS[key] - prior_counts.get(key, 0) for key in _COUNTS})
        checkpoint.write_text(json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(dict(completed=job["key"], bytes=result["complete_pdf_bytes"],
                              old_bytes=old["complete_pdf_bytes"], image_streams=encoded_images)), flush=True)
        return evidence
    finally:
        study.streams._brotli = previous_encoder
        study.pipeline._ENCODE_WORKDIR.reset(work)
        study.pipeline._STREAM_POLICY.reset(policy)
        study.pipeline._BROTLI_DECLARATION.reset(declaration)


def inventory():
    publication, ffpr, images, native = [json.loads(path.read_text())
                                         for path in (PUBLICATION, FFPR, IMAGE, NATIVE)]
    records = publication["records"] + publication["extras"]
    for pair in publication["native_pairs"] + ffpr["pairs"]:
        records += [pair[role] for role in ("reference", "candidate")]
    for row in images:
        for item in row["results"]:
            records.append(dict(case=dict(row, recipe={},
                bases={item["variant"]: dict(pdf=item["pdf"], sha256=item["pdf_sha256"])}),
                result=dict(item, image_variant=item["variant"], native_policy="flate"),
                origin=str(IMAGE), scope="image-component"))
    for row in native:
        for item in row["results"]:
            if not item["policy"].startswith("brotli"):
                continue
            source = Path(row["source"])
            pdf = NATIVE.parent / f"{source.stem}.{item['policy']}.pdf"
            records.append(dict(case=dict(source=str(source), input_sha256=file_hash(source),
                                           mode="passthrough", recipe={}),
                result=dict(item, pdf=str(pdf), pdf_sha256=file_hash(pdf),
                            image_variant="preserve-images", native_policy=item["policy"]),
                origin=str(NATIVE), scope="native-component"))
    selected = {}
    for record in records:
        r = record["result"]
        if not (r["native_policy"].startswith("brotli") or r["image_variant"].startswith("brotli")):
            continue
        path = r["pdf"]
        if path in selected:
            if selected[path]["result"]["pdf_sha256"] != r["pdf_sha256"]:
                raise ValueError("Conflicting measured source")
            continue
        if "exact_native" in r and not all(r.get(key) for key in
                ("exact_native", "exact_images", "exact_all_page_pixels")):
            raise ValueError("Unverified integrated source")
        if "decoded_samples_exact" in r and not (r["decoded_samples_exact"] and r["actual_pages_exact"]):
            raise ValueError("Unverified component source")
        selected[path] = dict(key=digest(path.encode())[:20], scope=record.get("scope", "integrated"),
            origin=record["origin"], original_record_sha256=digest(json.dumps(record, sort_keys=True).encode()),
            case={key: value for key, value in record["case"].items() if key in
                  ("source", "input_sha256", "mode", "dpi", "recipe", "prepared", "bases")},
            result={key: r[key] for key in
                    ("pdf", "pdf_sha256", "complete_pdf_bytes", "image_variant", "native_policy")})
    return list(selected.values())


def run(folder, workers=2, resume=False, reuse_verified=None):
    jobs = inventory()
    identity = dict(brotli_declaration=False, scope="all published integrated/image/native Brotli",
        inputs={str(path): file_hash(path) for path in (PUBLICATION, FFPR, IMAGE, NATIVE)},
        environment=study.environment(), implementation=file_hash(__file__),
        job_count=len(jobs), jobs_sha256=digest(json.dumps(jobs, sort_keys=True).encode()),
        verified_import=str(reuse_verified) if reuse_verified else None)
    folder.mkdir(parents=True, exist_ok=resume)
    frozen = folder / "identity.json"
    if frozen.exists() and json.loads(frozen.read_text()) != identity:
        raise ValueError("Changed rerun scope/implementation")
    frozen.write_text(json.dumps(identity, indent=2) + "\n")
    (folder / "jobs.json").write_text(json.dumps(jobs, indent=2) + "\n")
    (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    completed, errors = {}, {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(measure, job, folder / "jobs" / job["key"], identity, resume, reuse_verified): job
                   for job in jobs}
        for future in as_completed(futures):
            try:
                evidence = future.result()
                completed[evidence["job"]["result"]["pdf"]] = evidence
            except Exception as error:
                errors[futures[future]["key"]] = repr(error)
                print(json.dumps(dict(rejected=futures[future]["key"], error=repr(error))), flush=True)
            (folder / "metrics.json").write_text(json.dumps(dict(
                identity=identity, complete=len(completed) == len(jobs), errors=errors,
                results=completed), indent=2) + "\n")
    if errors:
        raise RuntimeError(f"Rejected {len(errors)} Brotli rerun outputs; see measured errors")
    print(f"BROTLI DEFAULT-OFF COMPLETE: {len(completed)} actual PDFs", flush=True)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True)
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--reuse-verified", type=Path, help="Pinned successful first-pass checkpoints only")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(Path(".tmp/compression-experiments") / args.label, args.workers, args.resume, args.reuse_verified)


if __name__ == "__main__":
    main()
