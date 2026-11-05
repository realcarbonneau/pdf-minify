"""Publish the completed JPEG XL experiment (TODO §§270/271); never estimate.

Audits both swap manifests (lossless BW/Indexed rows, lossy JPEG rows) and
the photo-match results (§314), writes `tests/fixtures/jxl_sizes.json`, then
fills only the measured cells of the page's tagged JPEG XL tables (§§282/283).
"""

import argparse
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bench_jxl as bench
from tools import benchmark_tables as tables

FIXTURE = Path("tests/fixtures/jxl_sizes.json")
LOSSLESS_ROWS = tuple(r[0] for r in bench.ROWS if r[4] == "lossless")
LOSSY_ROWS = tuple(r[0] for r in bench.ROWS if r[4] == "lossy")


def audit(lossless, lossy, photo_match):
    """Every row × document present once, unchanged and internally consistent."""
    baselines = bench.baseline_records()
    records = {}
    for manifest, rows in ((lossless, LOSSLESS_ROWS), (lossy, LOSSY_ROWS)):
        data = json.loads(Path(manifest).read_text())
        identity = data["identity"]
        if not data.get("complete") or identity["study"] != "JXL-SWAP-01" or identity["rows"] != sorted(rows):
            raise ValueError(f"Incomplete or wrong JPEG XL swap run: {manifest}")
        if identity["filter"] != bench.FILTER or identity["lossless_effort"] != bench.LOSSLESS_EFFORT:
            raise ValueError("Changed JPEG XL treatment settings")
        for r in data["records"]:
            key = r["row"], r["document"]
            base = baselines[key]
            if key in records:
                raise ValueError(f"Duplicate JPEG XL measurement: {key}")
            if (r["baseline_sha256"] != base["pdf_sha256"] or r["baseline_bytes"] != base["complete_pdf_bytes"]
                    or bench.file_digest(r["pdf"]) != r["pdf_sha256"]
                    or Path(r["pdf"]).stat().st_size != r["complete_pdf_bytes"]):
                raise ValueError(f"Changed baseline or treatment PDF: {key}")
            if r["treatment"] == "lossy" and any(i["quality"] is None for i in r["images"]):
                raise ValueError(f"Lossy treatment without a quality measurement: {key}")
            records[key] = r
    if set(records) != set(baselines):
        raise ValueError("The JPEG XL experiment does not cover every row and document")
    lossy_identity = json.loads(Path(lossy).read_text())["identity"]
    setting = dict(distance=lossy_identity["lossy_distance"], effort=lossy_identity["lossy_effort"],
                   whole_image=lossy_identity.get("lossy_whole_image"))
    match_identity = json.loads((Path(photo_match).parent / "identity.json").read_text())
    if setting["whole_image"] != list(bench.WHOLE_IMAGE) or match_identity.get("whole_image") != list(bench.WHOLE_IMAGE):
        raise ValueError("The JPEG rows and the photo match must both use whole-image encoding (§315)")
    chosen = bench.matched_setting(photo_match)
    if (chosen["distance"], chosen["effort"]) != (setting["distance"], setting["effort"]):
        raise ValueError("The JPEG rows do not use the photo-matched setting")
    cell = records[bench.MATCH]
    if {str(i["xref"]): i["jxl_sha256"] for i in cell["images"]} != chosen["jxl_sha256"]:
        raise ValueError("The published photo cell does not hold the matched JPEG XL images")
    return records, setting, {k: v for k, v in chosen.items() if k != "jxl_sha256"}


def fixture(lossless, lossy, photo_match):
    records, setting, matched = audit(lossless, lossy, photo_match)
    rows = []
    for row_id, *_ in bench.ROWS:
        cells = [records[row_id, d] for d in bench.DOCUMENTS]
        row = dict(row=row_id, treatment=cells[0]["treatment"],
                   baseline_bytes=[c["baseline_bytes"] for c in cells],
                   jxl_bytes=[c["complete_pdf_bytes"] for c in cells],
                   jxl_pdf_sha256=[c["pdf_sha256"] for c in cells],
                   images=[len(c["images"]) for c in cells])
        if row["treatment"] == "lossy":
            row["quality_gap"] = [statistics.fmean(i["quality"]["jxl_ssimulacra2"] - i["quality"]["jpeg_ssimulacra2"]
                                                   for i in c["images"]) if c["images"] else None
                                  for c in cells]
        rows.append(row)
    return dict(designer_rulings=[309, 310, 311, 313, 314, 315], filter=bench.FILTER,
                lossless_effort=bench.LOSSLESS_EFFORT, lossy_setting=setting, photo_match=matched,
                manifests={str(m): bench.file_digest(m) for m in (lossless, lossy, photo_match)},
                documents=list(bench.DOCUMENTS), rows=rows)


def percent(baseline, treatment):
    """Two decimals; bold only a displayed reduction, never +0.00% (§§248/249)."""
    value = 100 * (treatment - baseline) / baseline
    text = f"{value:+.2f}%"
    if text in ("+0.00%", "-0.00%"):
        return "+0.00%"
    return f"**{text}**" if value < 0 else text


def gap(value):
    """One decimal; a gap that rounds to zero is +0.0, never -0.0."""
    text = f"{value:+.1f}"
    return "+0.0" if text == "-0.0" else text


def values(proof):
    if proof["documents"] != list(bench.DOCUMENTS) or [r["row"] for r in proof["rows"]] != [r[0] for r in bench.ROWS]:
        raise ValueError("Wrong JPEG XL fixture scope")
    effect, sizes, gaps = {}, {}, {}
    for row in proof["rows"]:
        if any(type(n) is not int or n <= 0 for n in row["baseline_bytes"] + row["jxl_bytes"]):
            raise ValueError("JPEG XL publication requires measured integer sizes")
        effect[row["row"]] = [percent(b, t) for b, t in zip(row["baseline_bytes"], row["jxl_bytes"], strict=True)]
        sizes[row["row"]] = [f"{n:,}" for n in row["jxl_bytes"]]
        if row["treatment"] == "lossy":
            gaps[row["row"]] = ["no images" if g is None else gap(g) for g in row["quality_gap"]]
    return effect, sizes, gaps


def fill(markdown, proof):
    effect, sizes, gaps = values(proof)
    markdown = tables.fill(markdown, "jxl-effect", effect)
    markdown = tables.fill(markdown, "jxl-bytes", sizes)
    return tables.fill(markdown, "jxl-quality-gap", gaps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lossless", type=Path)
    parser.add_argument("lossy", type=Path)
    parser.add_argument("photo_match", type=Path, help="results.jsonl of `bench_jxl.py match`")
    args = parser.parse_args()
    proof = fixture(args.lossless, args.lossy, args.photo_match)
    FIXTURE.write_text(json.dumps(proof, indent=2) + "\n")
    tables.PAGE.write_text(fill(tables.PAGE.read_text(), proof))


if __name__ == "__main__":
    main()
