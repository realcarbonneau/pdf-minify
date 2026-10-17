"""NATIVE-02: FFPR specialized images fixed, Brotli baseline vs Zopfli treatment.

Reuses verified Zopfli outputs; only missing residual-compression saves run.
Accounts measured stream/syntax bytes and diagnoses extension overhead with
metadata-only controls. No image preparation or image encoder is invoked.
"""

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import bench_residual_streams as residual

overview, study = residual.overview, residual.study
SECTION = "## FFPR residual compression — Zopfli versus Brotli baseline"
ROWS = tuple(row for row in residual.ROWS if row.family.endswith("-ffpr"))
LABELS = ("BW + JBIG2", "5 colors + layered JBIG2", "Color + JPEG q50",
          "Color + JPEG2000 lossy r192", "Color + JPEG2000 lossless")
BYTE_KEYS = ("images", "native", "container", "other_streams", "syntax")


def stream_accounting(path):
    """Exact partition of complete bytes, not a file-size estimate."""
    result = dict.fromkeys(BYTE_KEYS, 0)
    signatures = {"images": Counter(), "native": Counter()}
    with study.fitz.open(path) as doc:
        result["pages"] = len(doc)
        result["brotli_declaration"] = doc.xref_get_key(doc.pdf_catalog(), "Extensions/PDFa/ExtensionRevision")[1]
        native = set(study.streams.native_stream_xrefs(doc))
        result["native_decoded_bytes"] = sum(len(doc.xref_stream(x)) for x in native)
        for xref in range(1, doc.xref_length()):
            if not doc.xref_is_stream(xref):
                continue
            raw = doc.xref_stream_raw(xref)
            kind = ("images" if doc.xref_get_key(xref, "Subtype")[1] == "/Image" else
                    "native" if xref in native else
                    "container" if doc.xref_get_key(xref, "Type")[1] in ("/ObjStm", "/XRef") else "other_streams")
            result[kind] += len(raw)
            if kind in signatures:
                signatures[kind][study.digest(raw)] += 1
        result["complete_pdf_bytes"] = Path(path).stat().st_size
    result["syntax"] = result["complete_pdf_bytes"] - sum(result[k] for k in BYTE_KEYS if k != "syntax")
    result.update({kind + "_signature": sorted(values.items()) for kind, values in signatures.items()})
    return result


def account_pair(pair):
    before, after = (stream_accounting(pair[k]["result"]["pdf"]) for k in ("reference", "candidate"))
    if before["images_signature"] != after["images_signature"]:
        raise ValueError("FFPR A/B changed encoded image payloads")
    changes = {key: after[key] - before[key] for key in BYTE_KEYS}
    total = after["complete_pdf_bytes"] - before["complete_pdf_bytes"]
    if sum(changes.values()) != total:
        raise ValueError("Stream/syntax accounting does not equal complete-file change")
    return dict(brotli=before, zopfli=after, zopfli_minus_brotli=changes, complete_byte_change=total)


def effect_table(documents, rows, pairs):
    indexed = {}
    for pair in pairs:
        key = (pair["document"], pair["combination"]["family"])
        if key in indexed:
            raise ValueError("Duplicate FFPR compressor pair")
        indexed[key] = pair
    lines = ["| FFPR image encoding | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|" * len(documents)]
    labels = {row.family: label for row, label in zip(ROWS, LABELS)}
    for row in rows:
        cells = []
        for document in documents:
            key = (document.key, row.family)
            if key not in indexed:
                raise ValueError(f"Missing FFPR compressor pair: {key}")
            pair = indexed[key]
            residual.validate_pair(document, row, pair, reference_policy="brotli")
            a, b = (pair[k]["result"]["complete_pdf_bytes"] for k in ("reference", "candidate"))
            cells.append(overview.measured_effect_cell(a, b, show_size=False, places=5))
        lines.append("| " + labels.get(row.family, overview.display_label(row.label)) + " | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def metadata_control(pair, folder):
    """Keep Zopfli streams; add only the writer's Brotli declaration."""
    folder.mkdir(parents=True, exist_ok=True)
    case, variant = pair["candidate"]["case"], pair["combination"]["variant"]
    base = Path(case["bases"][variant]["pdf"])
    declared, target = folder / "declared-base.pdf", folder / "zopfli-with-brotli-declaration.pdf"
    if not target.exists():
        with study.images.open_for_id_change(base) as doc:
            study.streams._declare_brotli(doc)
            doc.save(declared, no_new_id=True)
        study.save_combination(declared, target, case, variant, "zopfli", folder)
    actual, original = stream_accounting(target), stream_accounting(pair["candidate"]["result"]["pdf"])
    if any(actual[k + "_signature"] != original[k + "_signature"] for k in ("images", "native")):
        raise ValueError("Metadata-only control changed encoded content")
    return dict(pdf=str(target), sha256=overview.file_digest(target),
                complete_pdf_bytes=actual["complete_pdf_bytes"],
                added_declaration_bytes=actual["complete_pdf_bytes"] - original["complete_pdf_bytes"],
                accounting=actual)


def measure(document, row, candidate, folder, identity, resume):
    pair = residual.measure_pair(document, row, candidate, None, folder, identity, resume,
                                 reference_policy="brotli")
    pair["accounting"] = account_pair(pair)
    return pair


def run(publication_path, folder, *, workers=2, resume=False):
    if not 1 <= workers <= 3:
        raise ValueError("Use one to three isolated benchmark workers")
    publication = json.loads(publication_path.read_text())
    native_path = next(Path(path) for path in publication["inputs"] if "native-residual" in path)
    if overview.file_digest(native_path) != publication["inputs"][str(native_path)]:
        raise ValueError("Changed frozen producing manifest")
    producer = json.loads(native_path.read_text())["identity"]["toolchain"]
    current = residual.shared.toolchain()
    if any(producer[key] != current[key] for key in ("environment", "packages", "binaries")):
        raise ValueError("Changed encoding implementation, packages or binaries")
    identity = dict(publication=str(publication_path), publication_sha256=overview.file_digest(publication_path),
                    producing_toolchain=producer, current_encoding=current["environment"],
                    implementation=overview.file_digest(__file__),
                    paired_helper=overview.file_digest(residual.__file__),
                    rows=[asdict(r) for r in ROWS], documents=[asdict(d) for d in overview.DOCUMENTS],
                    factor="FFPR residual encoder: Brotli baseline, Zopfli treatment")
    folder.mkdir(parents=True, exist_ok=resume)
    identity_path = folder / "identity.json"
    if identity_path.exists() and json.loads(identity_path.read_text()) != identity:
        raise ValueError("Changed FFPR study identity")
    identity_path.write_text(json.dumps(identity, indent=2) + "\n")
    (folder / "implementation.py").write_bytes(Path(__file__).read_bytes())
    index = {(r["document"], r["family"], r["result"]["image_variant"], r["result"]["native_policy"]): r
             for r in publication["records"]}
    pairs = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {}
        for document in sorted(overview.DOCUMENTS, key=lambda d: d.key != "art"):
            for row in ROWS:
                candidate = index[(document.key, row.family, row.variant, "zopfli")]
                overview.validate_record(candidate["case"], candidate["result"])
                destination = folder / "jobs" / document.key / row.family
                futures[pool.submit(measure, document, row, candidate, destination, identity,
                                    resume and destination.exists())] = (document.key, row.family)
        for future in as_completed(futures):
            pairs[futures[future]] = future.result()
            (folder / "metrics.json").write_text(json.dumps(dict(identity=identity,
                complete=len(pairs) == len(ROWS) * len(overview.DOCUMENTS), pairs=list(pairs.values())), indent=2) + "\n")
    ordered = [pairs[(d.key, r.family)] for d in overview.DOCUMENTS for r in ROWS]
    controls = {key: metadata_control(pairs[(key, "bw-ffpr")], folder / "controls" / key)
                for key in ("art", "native")}
    result = dict(identity=identity, complete=True, pairs=ordered, metadata_controls=controls)
    (folder / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    (folder / "effect.md").write_text(effect_table(overview.DOCUMENTS, ROWS, ordered))
    print(f"FFPR COMPRESSOR COMPARISON COMPLETE: {len(ordered)} verified pairs", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(args.publication, Path(".tmp/compression-experiments") / args.label,
        workers=args.workers, resume=args.resume)


if __name__ == "__main__":
    main()
