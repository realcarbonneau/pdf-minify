"""Publish fixed-q LOSSY-05 across every active table; no estimated sizes."""

import argparse
from copy import deepcopy
from dataclasses import asdict, replace
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import bench_lossy_controls as controls
from tools import bench_best_overview as best
from tools import bench_ffpr_compressors as ffpr

FIXTURE = Path("tests/fixtures/lossy_controls_sizes.json")
REPORT = Path("docs/INTEGRATED_COMPRESSION.md")
FAMILIES = {"jpeg-q50": "jpeg-q75", "jpx-r192": "jpx-q75",
            "jpeg-q50-ffpr": "jpeg-q75-ffpr", "jpx-r192-ffpr": "jpx-q75-ffpr"}


def current_label(label):
    return label.replace("JPEG2000 lossy r192", "JPEG2000 q75").replace("JPEG q50", "JPEG q75")


def current_recipe(recipe):
    return replace(recipe, family=FAMILIES.get(recipe.family, recipe.family),
                   variant=FAMILIES.get(recipe.variant, recipe.variant), label=current_label(recipe.label))


def row_for(proof, mode, force, policy):
    matches = [r for r in proof["rows"] if (r["mode"], r["force_raster"], r["policy"]) == (mode, force, policy)]
    if len(matches) != 1:
        raise ValueError("Missing or duplicate measured lossy control row")
    row = matches[0]
    if (len(row["sizes"]) != 6 or any(type(n) is not int or n <= 0 for n in row["sizes"])
            or row["label"] != controls.combination(mode, force, policy).label):
        raise ValueError("Invalid or mislabeled measured lossy control row")
    return row


def updated_fixed_row(old, proof):
    """Retain immutable old fixtures; overlay only freshly measured families."""
    row = deepcopy(old)
    if old["family"] not in FAMILIES:
        return row
    # These are fixed-policy controls, not new measurements of the old Best
    # result. Do not carry those old bytes/hashes under the new q75 label.
    row.pop("best", None)
    row.pop("pdf_sha256", None)
    mode, force = ("color" if old["family"].startswith("jpeg-") else "jpx"), old["family"].endswith("-ffpr")
    row.update(family=FAMILIES[old["family"]], variant=FAMILIES[old["variant"]], label=current_label(old["label"]))
    for policy in ("zopfli", "brotli"):
        measured = row_for(proof, mode, force, policy)
        row[policy] = measured["sizes"]
        row.setdefault("fixed_labels", {})[policy] = measured["label"]
    return row


def make_fixture(path):
    data = json.loads(path.read_text())
    identity = data.get("identity", {})
    if (not data.get("complete") or identity.get("environment") != controls.study.environment()
            or identity.get("implementation_sha256") != controls.lossy.file_digest(controls.__file__)
            or identity.get("jpx_quality_mapping") != controls.lossy.quality.JPX_QUALITY_MAPPING):
        raise ValueError("Incomplete or changed current lossy controls")
    baseline_path = Path(identity["baseline"])
    baseline = controls.load_baseline(baseline_path)
    if controls.lossy.file_digest(baseline_path) != identity["baseline_sha256"]:
        raise ValueError("Changed lossy baseline provenance")
    controls.validate_inventory(controls.lossy.DOCUMENTS, data["records"])
    sources = {(r["document"], r["mode"], r["force_raster"]): r for r in baseline["records"]}
    records = {}
    for row in data["records"]:
        document = next(d for d in controls.lossy.DOCUMENTS if d.key == row["document"])
        source = sources[row["document"], row["mode"], row["force_raster"]]
        source_hash = next(d["source_sha256"] for d in baseline["identity"]["documents"] if d["key"] == document.key)
        expected = controls.prepared_case(document, source, identity["baseline_sha256"], source_hash)
        if row["case"] != expected:
            raise ValueError("Control changed the verified current image preparation")
        job = json.loads(Path(row["origin"]).read_text())
        if (job["identity"]["environment"] != identity["environment"] or job["identity"]["case"] != expected
                or row["result"] not in job["results"]):
            raise ValueError("Control differs from its producing verification")
        if row.get('reused_from'):
            reuse=identity['jpeg_control_reuse']
            frozen=Path(reuse['manifest'])
            if controls.lossy.file_digest(frozen)!=reuse['sha256'] or row['mode']!='color':
                raise ValueError('Changed or mislabeled reused JPEG control provenance')
            old=json.loads(frozen.read_text())
            matches=[r for r in old['records'] if (r['document'],r['mode'],r['force_raster'],r['result']['native_policy'])==
                     (row['document'],'color',row['force_raster'],row['result']['native_policy'])]
            if len(matches)!=1 or row['reused_from']!=dict(reuse,record_sha256=controls.lossy.digest(json.dumps(matches[0],sort_keys=True).encode())):
                raise ValueError('Changed reused JPEG producing record')
            if any(row['result'][k]!=matches[0]['result'][k] for k in ('pdf','pdf_sha256','complete_pdf_bytes')):
                raise ValueError('Reused JPEG control changed its actual file')
        records[row["document"], row["mode"], row["force_raster"], row["result"]["native_policy"]] = row
    rows = []
    for force in (False, True):
        for mode in controls.lossy.MODES:
            for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli")):
                cells = [records[d.key, mode, force, policy] for d in controls.lossy.DOCUMENTS]
                rows.append(dict(mode=mode, force_raster=force, policy=policy,
                                 label=controls.combination(mode, force, policy).label,
                                 sizes=[r["result"]["complete_pdf_bytes"] for r in cells],
                                 pdf_sha256=[r["result"]["pdf_sha256"] for r in cells],
                                 base_sha256=[next(iter(r["case"]["bases"].values()))["sha256"] for r in cells]))
    accounting = []
    for document in controls.lossy.DOCUMENTS:
        for mode in controls.lossy.MODES:
            pair = dict(reference=records[document.key, mode, True, "brotli"],
                        candidate=records[document.key, mode, True, "zopfli"])
            partition = ffpr.account_pair(pair)
            accounting.append(dict(document=document.key, mode=mode, accounting=partition))
    return dict(designer_ruling=271, quality=75, dpi=300, jpx_quality_mapping=identity["jpx_quality_mapping"],
                measured_manifest=str(path), measured_manifest_sha256=controls.lossy.file_digest(path),
                baseline_sha256=identity["baseline_sha256"],
                unchanged_publication_sha256=best.PUBLICATION_SHA256,
                documents=[asdict(d) for d in controls.lossy.DOCUMENTS], rows=rows, ffpr_accounting=accounting)


def validate_proof(proof):
    if (proof.get("designer_ruling") != 271 or proof.get("quality") != 75 or proof.get("dpi") != 300
            or proof.get("jpx_quality_mapping") != controls.lossy.quality.JPX_QUALITY_MAPPING
            or proof.get("documents") != [asdict(d) for d in controls.lossy.DOCUMENTS]
            or len(proof.get("rows", [])) != 10):
        raise ValueError("Wrong current-standard controls fixture")
    for mode in controls.lossy.MODES:
        for force in (False, True):
            for policy in (("zopfli", "brotli", "flate") if force else ("zopfli", "brotli")):
                row_for(proof, mode, force, policy)


def rewrite_tables(text, proof):
    validate_proof(proof)
    section, subsection, updated, lines = "", "", 0, []
    bases = {(mode, force): ("Color FFPR + " if force else "") + ("JPEG q75" if mode == "color" else "JPEG2000 q75")
             for mode in controls.lossy.MODES for force in (False, True)}
    labels = {r["label"]: r for r in proof["rows"]}
    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            section, subsection = line.strip(), ""
        elif line.startswith("### "):
            subsection = line.strip()
        if not line.startswith("| "):
            lines.append(line)
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        label = current_label(cells[0])
        matching = next(((mode, force) for (mode, force), base in bases.items() if label == base), None)
        replacement = None
        if section == ffpr.SECTION and subsection.startswith("### Replace Brotli") and matching:
            mode, force = matching
            a, b = (row_for(proof, mode, force, p)["sizes"] for p in ("brotli", "zopfli"))
            replacement = [controls.overview.measured_effect_cell(x, y, show_size=False) for x, y in zip(a, b, strict=True)]
        elif label in labels and ((section == ffpr.SECTION and subsection.startswith("### Fixed-encoder controls"))
                                  or (section == "## Focused scenarios" and subsection.startswith("### Color photography"))):
            row = labels[label]
            peer = row_for(proof, row["mode"], row["force_raster"], "brotli" if row["policy"] == "zopfli" else "zopfli")
            indices = [2] if section == "## Focused scenarios" else range(6)
            replacement = [f"**{row['sizes'][i]:,}**" if row["sizes"][i] <= peer["sizes"][i]
                           else f"{row['sizes'][i]:,}" for i in indices]
        elif section == "## Native/residual streams — measured effect versus Flate reference" and label in labels:
            row = labels[label]
            if row["force_raster"] and row["policy"] == "zopfli":
                reference = row_for(proof, row["mode"], True, "flate")["sizes"]
                replacement = ([f"{n:,}" for n in reference] if subsection.startswith("### Measured reference") else
                               [controls.overview.measured_effect_cell(a, b) for a, b in zip(reference, row["sizes"], strict=True)])
        if replacement is not None:
            if len(replacement) != len(cells)-1:
                raise ValueError("Changed benchmark table column scope")
            line = "| " + label + " | " + " | ".join(replacement) + " |\n"
            updated += 1
        lines.append(line)
    if updated != 22:
        raise ValueError(f"Expected all 22 affected table rows, found {updated}")
    return "".join(lines)


def apply_current(text):
    """Late overlay for older publishers: never restore obsolete active rows."""
    return rewrite_tables(text, json.loads(FIXTURE.read_text())) if FIXTURE.exists() else text


def patch_files(files):
    parts = ["*** Begin Patch\n"]
    for path, after in files.items():
        path = Path(path)
        if path.exists():
            before = path.read_text()
            if before == after:
                continue
            parts.append(f"*** Update File: {path}\n")
            for line in list(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True)))[2:]:
                parts.append("@@\n" if line.startswith("@@") else line)
        else:
            parts.append(f"*** Add File: {path}\n")
            parts.extend("+" + line + "\n" for line in after.splitlines())
    parts.append("*** End Patch\n")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    proof = make_fixture(args.manifest)
    print(patch_files({FIXTURE: json.dumps(proof, indent=2) + "\n",
                       REPORT: rewrite_tables(REPORT.read_text(), proof)}), end="")


if __name__ == "__main__":
    main()
