"""Publish only completed LOSSY-06 lossy measurements; never estimate."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bench_lossy_quality as bench
from tools import benchmark_tables as tables

FIXTURE = Path("tests/fixtures/lossy_quality_sizes.json")
# (FFPR, mode, fixture label, row ID in the page's `overview` table)
LABELS = ((False, "color", "JPEG q75", "jpeg"),
          (False, "jpx", "JPEG2000 q75", "jpx-lossy"),
          (True, "color", "Color FFPR + JPEG q75", "jpeg-ffpr"),
          (True, "jpx", "Color FFPR + JPEG2000 q75", "jpx-lossy-ffpr"))


def native_resource_images(row, source):
    """Source-bound native opacity/font images are not page-artwork canvases.

    Reuse the established B112 validator: replaced painted source images may
    not survive through hidden owners, while native opacity/Type 3 resources
    must not be deleted or lossily rewritten to force one artwork codec.
    """
    payloads = {c["payload_sha256"] for c in row["canvases"]}
    expected_filter = "/DCTDecode" if row["mode"] == "color" else "/JPXDecode"
    protected = []
    with bench.fitz.open(source) as original, bench.fitz.open(row["pdf"]) as doc:
        original_images = {bench.digest(original.xref_stream_raw(x))
                           for x in range(1, original.xref_length())
                           if original.xref_is_stream(x) and original.xref_get_key(x, "Subtype")[1] == "/Image"}
        replacements = {image[0] for page in doc for image in page.get_images(full=True)}
        bench.overview.study.images.assert_no_retained_source_images(original, doc, replacements)
        for xref in range(1, doc.xref_length()):
            if not doc.xref_is_stream(xref) or doc.xref_get_key(xref, "Subtype")[1] != "/Image":
                continue
            fingerprint = bench.digest(doc.xref_stream_raw(xref))
            if xref in replacements:
                if doc.xref_get_key(xref, "Filter")[1] != expected_filter or fingerprint not in payloads:
                    raise ValueError("Painted image is not the verified production payload")
                if row["mode"] == "color":
                    actual_bytes = len(doc.xref_stream_raw(xref))
                    if any(c["quality_reference"]["jpeg_bytes"] != actual_bytes
                           for c in row["canvases"] if c["payload_sha256"] == fingerprint):
                        raise ValueError("Reference JPEG byte count differs from the actual saved payload")
            else:
                if row["force_raster"] or fingerprint not in original_images:
                    raise ValueError("Unverified non-artwork image resource")
                protected.append(dict(sha256=fingerprint, properties={key: doc.xref_get_key(xref, key)[1]
                                 for key in ("Width", "Height", "BitsPerComponent", "ColorSpace", "Filter", "Decode")}))
    return sorted(protected, key=lambda item: json.dumps(item, sort_keys=True))


def audit(manifest):
    data = json.loads(manifest.read_text())
    if (not data.get("complete") or data["identity"] != bench.identity(
            bench.DOCUMENTS, data['identity'].get('jpeg_reuse'))):
        raise ValueError("Incomplete or changed lossy study identity")
    # The run already decoded/rendered every page. Hash-verified immutable
    # outputs retain that proof; publication does not repeat all encoding or
    # all-page renders merely to format the same measurements.
    sources = {d.key: d.source for d in bench.DOCUMENTS}
    reuse=data['identity'].get('jpeg_reuse')
    imported={}
    if reuse:
        path=Path(reuse['manifest'])
        if bench.file_digest(path)!=reuse['sha256']:
            raise ValueError('Changed JPEG reuse publication provenance')
        imported={(r['document'],r['force_raster']):r for r in json.loads(path.read_text())['records'] if r['mode']=='color'}
    protected_pairs = {}
    for row in data["records"]:
        bench.verify_record(row, rerender=False)
        if reuse and row['mode']=='color':
            old=imported[row['document'],row['force_raster']]
            expected=dict(manifest=reuse['manifest'],manifest_sha256=reuse['sha256'],
                          record_sha256=bench.digest(json.dumps(old,sort_keys=True).encode()))
            if row.get('reused_from')!=expected or any(row[k]!=old[k] for k in
                    ('pdf','pdf_sha256','complete_pdf_bytes','readback','recipe')):
                raise ValueError('Changed reused JPEG producing measurement')
        protected = native_resource_images(row, sources[row["document"]])
        row["native_resource_images"] = protected
        key = row["document"], row["force_raster"]
        if key in protected_pairs and protected_pairs[key] != protected:
            raise ValueError("Lossy comparison changed protected native opacity/font images")
        protected_pairs[key] = protected
    bench.table(bench.DOCUMENTS, data["records"])  # full inventory and pair checks
    return data


def fixture(manifest):
    data = audit(manifest)
    records = {(r["document"], r["force_raster"], r["mode"]): r for r in data["records"]}
    rows = []
    for force, mode, label, _ in LABELS:
        cells = [records[d.key, force, mode] for d in bench.DOCUMENTS]
        rows.append(dict(label=label, mode=mode, force_raster=force,
                         sizes=[r["complete_pdf_bytes"] for r in cells],
                         pdf_sha256=[r["pdf_sha256"] for r in cells],
                         canvas_proof_sha256=[bench.digest(json.dumps(r["canvases"], sort_keys=True).encode())
                                              for r in cells],
                         readback_proof_sha256=[bench.digest(json.dumps(r["readback"], sort_keys=True).encode())
                                                for r in cells],
                         native_resource_image_count=[len(r["native_resource_images"]) for r in cells],
                         native_resource_proof_sha256=[bench.digest(json.dumps(r["native_resource_images"], sort_keys=True).encode())
                                                      for r in cells]))
    return dict(designer_rulings=[272, 278, 284], quality=bench.QUALITY, dpi=bench.DPI,
                visual_quality_basis=data["identity"]["visual_quality_basis"],
                jpeg_profile=data["identity"]["jpeg_profile"], jpx_profile=data["identity"]["jpx_profile"],
                jpx_quality_mapping=data["identity"]["jpx_quality_mapping"],
                jpeg_reuse=data['identity'].get('jpeg_reuse'),
                measured_manifest=str(manifest), measured_manifest_sha256=bench.file_digest(manifest),
                documents=[asdict(d) for d in bench.DOCUMENTS],
                source_sha256=[d["source_sha256"] for d in data["identity"]["documents"]], rows=rows)


def overview_values(proof):
    """Value cells of the four lossy `overview` rows, keyed by row ID.

    Bold marks the smaller (or tied) codec of each JPEG/JPEG2000 pair at the
    same native/FFPR fidelity; the lossless reference is a separate group.
    """
    if (proof["quality"] != 75 or proof["dpi"] != 300 or len(proof["rows"]) != 4
            or proof["documents"] != [asdict(d) for d in bench.DOCUMENTS]
            or proof.get("jpx_quality_mapping") != bench.quality.JPX_QUALITY_MAPPING
            or proof.get("visual_quality_basis") != "jpx-calibrated-to-jpeg-median-ssimulacra2"):
        raise ValueError("Wrong lossy baseline fixture scope")
    rows = {}
    for (force, mode, label, _), row in zip(LABELS, proof["rows"], strict=True):
        if (row["label"], row["mode"], row["force_raster"]) != (label, mode, force):
            raise ValueError("Mislabeled lossy fixture row")
        if len(row["sizes"]) != 6 or any(type(n) is not int or n <= 0 for n in row["sizes"]):
            raise ValueError("Lossy publication requires six measured integer sizes")
        rows[label] = row
    values = {}
    for force, mode, label, row_id in LABELS:
        peer = next(row for row in rows.values() if row["force_raster"] == force and row["mode"] != mode)
        values[row_id] = [f"**{n:,}**" if n <= p else f"{n:,}"
                          for n, p in zip(rows[label]["sizes"], peer["sizes"], strict=True)]
    return values


def fill_overview(markdown, proof):
    """Write only the four lossy rows' measured cells into the `overview` table."""
    return tables.fill(markdown, "overview", overview_values(proof))


def current_overview_values():
    """The pinned current lossy rows, or nothing before that fixture exists."""
    return overview_values(json.loads(FIXTURE.read_text())) if FIXTURE.exists() else {}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    proof = fixture(args.manifest)
    # Emit an apply_patch; tracked files are edited only with apply_patch.
    from tools.publish_lossy_controls import patch_files
    print(patch_files({FIXTURE: json.dumps(proof, indent=2)+'\n'}), end='')


if __name__ == "__main__":
    main()
