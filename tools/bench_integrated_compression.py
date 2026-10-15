"""Integrated image × native compression: validated complete PDFs, size only."""

import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pymupdf as fitz

from pdf_minimalist.core import pipeline, stream_compression as streams
from tools import bench_image_streams as images


POLICIES = ("flate", "zopfli", "brotli")
VARIANTS = tuple(v for v in images.VARIANTS if v != "current-flate")
CODES = dict(zip(VARIANTS, ("F", "F+", "Z", "Z+", "B", "B+", "J")))
NATIVE_CODES = dict(zip(POLICIES, ("F", "Z", "B")))
ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def environment():
    files = ("pdf_minimalist/core/pipeline.py", "pdf_minimalist/core/stream_compression.py",
             "pdf_minimalist/core/display.py", "tools/bench_integrated_compression.py")
    return dict(python=sys.version.split()[0], pymupdf=fitz.VersionBind,
                zopfli=pipeline.zopfli_binary(),
                implementation={name: digest((ROOT / name).read_bytes()) for name in files})


def snapshot(path, dpi):
    """Actual native/image bytes, complete page geometry and all-page pixels."""
    prior = fitz.TOOLS.mupdf_warnings()
    with fitz.open(path) as doc:
        bitmap = Counter()
        for xref in range(1, doc.xref_length()):
            if not doc.xref_is_stream(xref) or doc.xref_get_key(xref, "Subtype")[1] != "/Image":
                continue
            properties = tuple(canonical_value(doc, doc.xref_get_key(xref, key)[1]) for key in
                               ("Filter", "Width", "Height", "BitsPerComponent",
                                "ImageMask", "DecodeParms", "ColorSpace", "Interpolate"))
            bitmap[(digest(doc.xref_stream_raw(xref)), digest(doc.xref_stream(xref)), properties)] += 1
        native = Counter(digest(doc.xref_stream(xref)) for xref in streams.native_stream_xrefs(doc))
        byte_warnings = fitz.TOOLS.mupdf_warnings()
        if byte_warnings:
            raise RuntimeError(f"Stream decoding diagnostics: {byte_warnings}")
        pages, diagnostics = [], []
        for page in doc:
            pages.append(images.page_signature(page, dpi))
            diagnostics.append(fitz.TOOLS.mupdf_warnings())
        return dict(images=sorted((repr(key), value) for key, value in bitmap.items()),
                    native=sorted(native.items()), pages=pages,
                    metadata={key: value for key, value in doc.metadata.items() if key != "format"},
                    toc=doc.get_toc(), attachments=[(name, digest(doc.embfile_get(name)))
                                                   for name in doc.embfile_names()],
                    diagnostics=diagnostics, prior_diagnostics=prior)


def canonical_value(doc, value, seen=()):
    """Compare image properties semantically, independent of saved xref IDs."""
    def reference(match):
        xref = int(match[1])
        if xref in seen:
            raise ValueError("Cyclic image decoding property")
        if doc.xref_is_stream(xref):
            properties = {key: canonical_value(doc, doc.xref_get_key(xref, key)[1], (*seen, xref))
                          for key in doc.xref_get_keys(xref) if key not in ("Length", "Filter", "DecodeParms")}
            return json.dumps(dict(decoded=digest(doc.xref_stream(xref)), properties=properties), sort_keys=True)
        return canonical_value(doc, doc.xref_object(xref, compressed=True), (*seen, xref))
    return re.sub(r"\b(\d+)\s+\d+\s+R\b", reference, value)


def verify(path, expected, dpi, policy):
    actual = snapshot(path, dpi)
    for key in ("images", "native", "pages", "metadata", "toc", "attachments"):
        if actual[key] != expected[key]:
            raise RuntimeError(f"Integrated {policy} output changed {key}: {path}")
    for before, after in zip(expected["diagnostics"], actual["diagnostics"]):
        if images.diagnostic_messages(after) - images.diagnostic_messages(before):
            raise RuntimeError(f"New page diagnostics: {after}")
    known = images.diagnostic_messages(expected["prior_diagnostics"])
    for message in expected["diagnostics"]:
        known |= images.diagnostic_messages(message)
    if images.diagnostic_messages(actual["prior_diagnostics"]) - known:
        raise RuntimeError(f"New pre-validation diagnostics: {actual['prior_diagnostics']}")
    with fitz.open(path) as doc:
        for xref in streams.native_stream_xrefs(doc):
            data = doc.xref_stream(xref)
            wanted = "null" if not data else "/BrotliDecode" if policy == "brotli" else "/FlateDecode"
            if doc.xref_get_key(xref, "Filter")[1] != wanted:
                raise RuntimeError(f"Wrong actual native filter: {path}, {xref}")
        if policy == "brotli":
            if doc.xref_get_key(doc.pdf_catalog(), "Extensions/PDFa/ExtensionRevision")[1] != "2026":
                raise RuntimeError("Missing Brotli extension declaration")
    return dict(page_diagnostics=actual["diagnostics"],
                pre_validation_diagnostics=actual["prior_diagnostics"])


def save_combination(base, target, case, variant, policy, folder):
    """Use the real shared native/font/container saver for every matrix cell."""
    work = pipeline._ENCODE_WORKDIR.set(str(folder))
    native = pipeline._STREAM_POLICY.set(policy)
    try:
        with images.open_for_id_change(base) as doc:
            images.set_pdf_id(doc, case["input_sha256"], case.get("prepared", case["recipe"]),
                              f"integrated:{variant}:{policy}")
            # Preparation already performed font subsetting. Repeating it
            # rewrites TrueType checksum bytes even without changing glyphs.
            pipeline._save_optimized_pdf(doc, str(target), no_new_id=True, subset_fonts=False)
    finally:
        pipeline._STREAM_POLICY.reset(native)
        pipeline._ENCODE_WORKDIR.reset(work)


def run_case(case, folder, *, policies=POLICIES, resume=False):
    folder.mkdir(parents=True, exist_ok=resume)
    expected_identity = dict(case=case, environment=environment(), policies=list(policies))
    checkpoint = folder / "metrics.json"
    previous = json.loads(checkpoint.read_text()) if resume and checkpoint.exists() else None
    if previous and previous["identity"] != expected_identity:
        raise ValueError("Refusing changed integrated input/environment/policies")
    old = {(r["image_variant"], r["native_policy"]): r for r in previous["results"]} if previous else {}
    report = dict(identity=expected_identity, results=[])
    source = Path(case["source"])
    if digest(source.read_bytes()) != case["input_sha256"]:
        raise ValueError("Changed original source PDF")
    for variant, base_info in case["bases"].items():
        base = Path(base_info["pdf"])
        if digest(base.read_bytes()) != base_info["sha256"]:
            raise ValueError("Changed prepared image artifact")
        expected = snapshot(base, case["dpi"])
        for policy in policies:
            target = folder / f"{variant}--native-{policy}.pdf"
            prior = old.get((variant, policy))
            reused = bool(resume and target.exists() and prior)
            if reused:
                if (target.stat().st_size != prior["complete_pdf_bytes"] or
                        digest(target.read_bytes()) != prior["pdf_sha256"]):
                    raise ValueError("Changed saved integrated artifact")
            else:
                if target.exists():
                    raise FileExistsError(f"Unowned existing output: {target}")
                save_combination(base, target, case, variant, policy, folder)
            diagnostics = verify(target, expected, case["dpi"], policy)
            result = dict(image_variant=variant, native_policy=policy,
                          complete_pdf_bytes=target.stat().st_size,
                          pdf_sha256=digest(target.read_bytes()), pdf=str(target),
                          exact_images=True, exact_native=True, exact_all_page_pixels=True,
                          source_page_diagnostics=expected["diagnostics"],
                          source_pre_validation_diagnostics=expected["prior_diagnostics"],
                          output_page_diagnostics=diagnostics["page_diagnostics"],
                          pre_validation_diagnostics=diagnostics["pre_validation_diagnostics"],
                          reused=reused)
            report["results"].append(result)
            checkpoint.write_text(json.dumps(report, indent=2)+"\n")
            print(json.dumps(dict(case=case["id"], image=variant, native=policy,
                                  complete_pdf_bytes=result["complete_pdf_bytes"], reused=reused)), flush=True)
    return report


def bitmap_cases(manifest):
    for item in json.loads(manifest.read_text()):
        case = {key: item[key] for key in ("source", "input_sha256", "mode", "dpi", "colors",
                                         "threshold_method", "threshold", "prepared")}
        case["recipe"] = {key: case[key] for key in ("mode", "dpi", "colors", "threshold_method", "threshold")}
        case["id"] = Path(item["results"][0]["pdf"]).parent.name
        case["family"] = "paired-bitmap"
        case["bases"] = {r["variant"]: dict(pdf=r["pdf"], sha256=r["pdf_sha256"])
                         for r in item["results"] if r["variant"] in VARIANTS}
        if set(case["bases"]) != set(VARIANTS):
            raise ValueError("Incomplete seven-variant bitmap preparation")
        yield case


def production_cases(sources, folder, resume=False, *, native_sources=None):
    recipes = (
        ("jpeg-q50", dict(mode="color", dpi_cap=150, jpeg_q=50)),
        ("jpx-r192", dict(mode="jpx", dpi_cap=150, rate=192, lossless=False)),
        ("jpx-lossless", dict(mode="jpx", dpi_cap=150, lossless=True)),
        ("preserve-images", dict(mode="passthrough")),
    )
    extra_native = [Path("examples") / name for name in (
        "models-nasa-kepler.pdf", "deed-brevard.pdf", "form-fw9.pdf", "form-941-2026.pdf")]
    fixture = Path(".tmp/native-stream-compression/main/native-text-vector-font.pdf")
    if fixture.exists():
        extra_native.append(fixture)
    if native_sources is not None:
        extra_native = native_sources
    for source, selected in [(source, recipes) for source in sources] + [
            (source, recipes[-1:]) for source in extra_native]:
        for variant, recipe in selected:
            case_id = f"{source.stem}.{variant}"
            prep = folder / "prepared" / case_id
            prep.mkdir(parents=True, exist_ok=resume)
            base = prep / "base.pdf"
            identity = dict(source=str(source), input_sha256=digest(source.read_bytes()), recipe=recipe,
                            environment=environment())
            meta = prep / "identity.json"
            if resume and base.exists() and meta.exists():
                previous = json.loads(meta.read_text())
                if previous["identity"] != identity or previous["sha256"] != digest(base.read_bytes()):
                    raise ValueError("Changed production preparation")
            else:
                if base.exists():
                    raise FileExistsError(base)
                pipeline.save_with_spec(str(source), str(base), recipe, workdir=str(prep))
                meta.write_text(json.dumps(dict(identity=identity, sha256=digest(base.read_bytes())), indent=2)+"\n")
            print(json.dumps(dict(prepared=case_id, recipe=recipe)), flush=True)
            yield dict(id=case_id, family="production", source=str(source),
                       input_sha256=identity["input_sha256"], mode=recipe["mode"], dpi=150,
                       recipe=recipe, bases={variant: dict(pdf=str(base), sha256=digest(base.read_bytes()))})


def import_production(folder):
    """Explicit import of frozen preparations, retaining their prior provenance.

    This is not resume across changed code: the new run records both the
    preparation's implementation and the current native/save implementation.
    """
    for meta in sorted(folder.glob("*/identity.json")):
        stored = json.loads(meta.read_text())
        identity, base = stored["identity"], meta.parent / "base.pdf"
        source, recipe = Path(identity["source"]), identity["recipe"]
        if digest(source.read_bytes()) != identity["input_sha256"] or digest(base.read_bytes()) != stored["sha256"]:
            raise ValueError("Changed imported preparation/source")
        if recipe["mode"] == "color" and recipe.get("jpeg_q") == 50:
            variant = "jpeg-q50"
        elif recipe["mode"] == "jpx" and recipe.get("lossless"):
            variant = "jpx-lossless"
        elif recipe["mode"] == "jpx" and recipe.get("rate") == 192:
            variant = "jpx-r192"
        elif recipe["mode"] == "passthrough":
            variant = "preserve-images"
        else:
            raise ValueError("Unsupported imported image recipe")
        yield dict(id=meta.parent.name, family="production", source=str(source),
                   input_sha256=identity["input_sha256"], mode=recipe["mode"], dpi=150,
                   recipe=recipe, preparation_environment=identity["environment"],
                   bases={variant: dict(pdf=str(base), sha256=stored["sha256"])})


def title(case):
    source = Path(case["source"]).stem.replace("paper-arxiv-1406.2661", "GAN").replace("scan-", "")
    if case["family"] == "production":
        return f"{source} / {next(iter(case['bases']))}"
    if case["mode"] == "indexed":
        return f"{source} / {case['dpi']}dpi / {case['colors']} colors"
    threshold = case["threshold_method"] if case["threshold"] is None else f"T={case['threshold']}"
    return f"{source} / {case['mode']} / {case['dpi']}dpi / {threshold}"


def matrix_markdown(reports):
    output = []
    for family in ("paired-bitmap", "production"):
        group = [row for row in reports if row["identity"]["case"]["family"] == family]
        if not group:
            continue
        combos = [(variant, policy) for variant in VARIANTS for policy in POLICIES] if family == "paired-bitmap" else [(None, policy) for policy in POLICIES]
        headers = [f"{CODES[v]}/{NATIVE_CODES[p]}" if v else NATIVE_CODES[p] for v, p in combos]
        output += ["### Paired bitmap × native policies" if family == "paired-bitmap" else "### Other production image recipes × native policies", "",
                   "| Complete input / explicit recipe | " + " | ".join(headers) + " |",
                   "|---|" + "---:|"*len(headers)]
        for report in group:
            case = report["identity"]["case"]
            sizes = {(r["image_variant"], r["native_policy"]): r["complete_pdf_bytes"] for r in report["results"]}
            values = [sizes[(v or next(iter(case["bases"])), p)] for v, p in combos]
            best = min(values)
            cells = [f"**{v:,}**" if v == best else f"{v:,}" for v in values]
            output.append("| " + title(case) + " | " + " | ".join(cells) + " |")
        output.append("")
    return "\n".join(output)


def export(reports, folder):
    (folder / "matrix.md").write_text(matrix_markdown(reports)+"\n")
    with (folder / "matrix.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("source", "case", "recipe", "image_encoding", "native_encoding", "complete_pdf_bytes", "pdf", "pdf_sha256"))
        for report in reports:
            case = report["identity"]["case"]
            for result in report["results"]:
                writer.writerow((case["source"], case["id"], json.dumps(case["recipe"], sort_keys=True),
                                 result["image_variant"], result["native_policy"], result["complete_pdf_bytes"],
                                 result["pdf"], result["pdf_sha256"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bitmap-manifest", type=Path, default=Path(".tmp/image-stream-compression/size-20261015/metrics.json"))
    parser.add_argument("--label", default="size-20261015")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--paired-only", action="store_true")
    parser.add_argument("--prepared-production", type=Path,
                        help="Explicitly import hash-verified frozen production preparations")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    folder = Path(".tmp/integrated-compression") / args.label
    folder.mkdir(parents=True, exist_ok=args.resume)
    jobs = list(bitmap_cases(args.bitmap_manifest))
    sources = list(dict.fromkeys(Path(case["source"]) for case in jobs))
    if args.prepared_production and args.paired_only:
        parser.error("--prepared-production and --paired-only are mutually exclusive")
    if args.prepared_production:
        jobs += list(import_production(args.prepared_production))
    elif not args.paired_only:
        jobs += list(production_cases(sources, folder, args.resume))
    reports = []
    for case in jobs:
        reports.append(run_case(case, folder / case["id"], resume=args.resume))
        (folder / "metrics.json").write_text(json.dumps(reports, indent=2)+"\n")
        export(reports, folder)
    print("INTEGRATED COMPLETE-PDF SIZE MATRIX GREEN", flush=True)


if __name__ == "__main__":
    main()
