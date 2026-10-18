"""Measure the Best-only overview from frozen, verified image preparations.

Fixed-encoder measurements remain immutable binary controls. This tool uses
the production Best saver, not minima copied from those controls. No image
preparation, J* encoding or compute-time comparison is performed.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import sys

for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[name] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pdf_minify.core import best_streams as best
from tools import bench_compression_overview as overview

study = overview.study
PUBLICATION = Path(".tmp/compression-experiments/brotli-default-off-publication-20261017/publication.json")
PUBLICATION_SHA256 = "9279a171feff32151a44e7d2f41d3042abdc611bdd2ecf72c3b4bb724eeed22d"


@dataclass(frozen=True)
class Recipe:
    key: str
    label: str
    family: str
    variant: str
    section: str


REFERENCE = "Unresampled reference"
BW = "Black and white (BW + Otsu)"
INDEXED = "Indexed color — low palettes"
COLOR = "Full color"
RECIPES = (
    Recipe("reference", "Unresampled reference", "preserve-images", "preserve-images", REFERENCE),
    Recipe("bw-jbig2", "BW + JBIG2", "bw-images", "jbig2", BW),
    Recipe("bw-packed", "BW + packed samples", "bw-images", "zopfli-plain", BW),
    Recipe("bw-ffpr-jbig2", "BW FFPR + JBIG2", "bw-ffpr", "jbig2", BW),
    Recipe("bw-ffpr-packed", "BW FFPR + packed samples", "bw-ffpr", "zopfli-plain", BW),
    Recipe("indexed-jbig2", "Indexed 5 colors + colored JBIG2", "indexed", "jbig2", INDEXED),
    Recipe("indexed-5", "Indexed 5 colors", "indexed", "zopfli-plain", INDEXED),
    Recipe("indexed-16", "Indexed 16 colors", "indexed-16", "zopfli-plain", INDEXED),
    Recipe("indexed-64", "Indexed 64 colors", "indexed-64", "zopfli-plain", INDEXED),
    Recipe("indexed-ffpr-jbig2", "Color FFPR; indexed 5 colors + colored JBIG2", "indexed-ffpr", "jbig2", INDEXED),
    Recipe("indexed-ffpr-5", "Color FFPR; indexed 5 colors", "indexed-ffpr", "zopfli-plain", INDEXED),
    Recipe("indexed-ffpr-16", "Color FFPR; indexed 16 colors", "indexed-ffpr-16", "zopfli-plain", INDEXED),
    Recipe("indexed-ffpr-64", "Color FFPR; indexed 64 colors", "indexed-ffpr-64", "zopfli-plain", INDEXED),
    Recipe("jpeg", "JPEG q50", "jpeg-q50", "jpeg-q50", COLOR),
    Recipe("jpx-lossy", "JPEG2000 lossy r192", "jpx-r192", "jpx-r192", COLOR),
    Recipe("jpx-lossless", "JPEG2000 lossless", "jpx-lossless", "jpx-lossless", COLOR),
    Recipe("jpeg-ffpr", "Color FFPR + JPEG q50", "jpeg-q50-ffpr", "jpeg-q50-ffpr", COLOR),
    Recipe("jpx-lossy-ffpr", "Color FFPR + JPEG2000 lossy r192", "jpx-r192-ffpr", "jpx-r192-ffpr", COLOR),
    Recipe("jpx-lossless-ffpr", "Color FFPR + JPEG2000 lossless", "jpx-lossless-ffpr", "jpx-lossless-ffpr", COLOR),
)


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as source:
        while data := source.read(1024 * 1024):
            hasher.update(data)
    return hasher.hexdigest()


def load_publication(path=PUBLICATION):
    if digest(path) != PUBLICATION_SHA256:
        raise ValueError("Changed frozen fixed-encoder publication")
    return json.loads(Path(path).read_text())


def fixed_records(publication):
    records = list(publication["records"])
    records += [pair[role] for pair in publication["ffpr_pairs"]
                for role in ("reference", "candidate")]
    index = {}
    for record in records:
        result = record["result"]
        key = (record["document"], record["family"], result["image_variant"], result["native_policy"])
        if key in index and index[key]["result"] != result:
            raise ValueError(f"Conflicting fixed-encoder measurement: {key}")
        index[key] = record
    return index


def fixed_pair(document, recipe, index):
    records = []
    for policy in ("brotli", "zopfli"):
        variant = recipe.variant.replace("zopfli-", f"{policy}-", 1)
        key = (document.key, recipe.family, variant, policy)
        if key not in index:
            raise ValueError(f"Missing fixed-encoder measurement: {key}")
        record = index[key]
        if record["case"]["source"] != document.source:
            raise ValueError("Wrong source in fixed-encoder measurement")
        records.append(record)
    fields = ("source", "input_sha256", "mode", "dpi", "recipe", "prepared")
    if any(records[0]["case"].get(key) != records[1]["case"].get(key) for key in fields):
        raise ValueError("Fixed-encoder comparison changes preparation or recipe")
    return tuple(records)


def semantic_graph(doc, *, include_ids=True):
    """Lossless document graph, ignoring ONLY eligible stream storage choices.

    Includes binary IDs, native content/fonts, decoded eligible image samples,
    exact J*/other payloads, predictors, links, tags, attachments and metadata.
    Native/sample filters and derived Length are not visual content. An absent
    DecodeParms and a PDF null are semantically the same. This graph proof
    reuses the frozen preparation's all-page render checks, not new renders.
    """
    m = study.fitz.mupdf
    native = m.pdf_document_from_fz_document(doc.this)
    eligible = {xref for xref, _ in best._eligible_xrefs(doc)}
    seen = {}

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
            storage = stream_xref in eligible
            ignored = {"Length", "Filter"} if storage else {"Length"} if stream_xref else set()
            values = [[name, visit(items[name])] for name in sorted(items)
                      if name not in ignored and not (storage and name == "DecodeParms"
                                                       and m.pdf_is_null(items[name]))]
            if stream_xref is not None:
                payload = doc.xref_stream(stream_xref) if storage else doc.xref_stream_raw(stream_xref)
                return ["stream", values, hashlib.sha256(payload).hexdigest()]
            return ["dict", values]
        if m.pdf_is_array(obj):
            return ["array", [visit(m.pdf_array_get(obj, i)) for i in range(m.pdf_array_len(obj))]]
        return ["value", m.pdf_sprint_obj(None, 0, obj, True, True)[0]]

    trailer = m.pdf_trailer(native)
    keys = ("Root", "Info", "ID", "Encrypt") if include_ids else ("Root", "Info", "Encrypt")
    graph = [visit(m.pdf_dict_gets(trailer, key)) for key in keys]
    return hashlib.sha256(json.dumps(graph, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def identity(publication_path):
    environment = study.environment()
    for name in ("pdf_minify/core/best_streams.py", "tools/bench_best_overview.py"):
        environment["implementation"][name] = digest(name)
    return dict(publication=str(publication_path), publication_sha256=digest(publication_path),
                environment=environment, recipes=[asdict(r) for r in RECIPES],
                documents=[asdict(d) for d in overview.DOCUMENTS],
                stream_policy="best", image_prediction="preserve", brotli_declaration=False)


def validate_measured(record):
    result = record["result"]
    if (result.get("stream_policy") != "best" or result.get("brotli_declaration") is not False
            or not result.get("exact_semantic_graph") or result.get("validation_error")):
        raise ValueError("Missing verified Best measurement")
    path = Path(result["pdf"])
    if digest(path) != result["pdf_sha256"] or path.stat().st_size != result["complete_pdf_bytes"]:
        raise ValueError("Changed measured Best PDF")
    if (result["complete_pdf_bytes"] != result["selection"]["file_bytes"] or
            result["complete_pdf_bytes"] != min(result["selection"]["candidate_bytes"].values())):
        raise ValueError("Best size is not its actual saved candidate minimum")


def measure(document, recipe, seed, folder, expected_identity, resume=False):
    """A separate actual save per recipe/input, including no-image controls."""
    overview.validate_record(seed["case"], seed["result"])
    case = seed["case"]
    if case["source"] != document.source:
        raise ValueError("Wrong source preparation")
    base = case["bases"][recipe.variant]
    job = dict(document=asdict(document), recipe=asdict(recipe),
               preparation=base, seed_pdf=seed["result"]["pdf"], seed_sha256=seed["result"]["pdf_sha256"])
    folder = Path(folder)
    checkpoint = folder / "metrics.json"
    if resume and checkpoint.exists():
        prior = json.loads(checkpoint.read_text())
        if prior["identity"] != expected_identity or prior["job"] != job:
            raise ValueError("Refusing changed Best input/preparation/implementation resume")
        validate_measured(prior)
        return prior
    folder.mkdir(parents=True, exist_ok=resume)
    target = folder / "best.pdf"
    if target.exists():
        raise FileExistsError(f"Unowned existing Best output: {target}")
    with study.images.open_for_id_change(base["pdf"]) as doc:
        study.images.set_pdf_id(doc, case["input_sha256"], case.get("prepared", case["recipe"]),
                                f"integrated-best:{recipe.key}")
        expected_graph = semantic_graph(doc)
        # Preparation already subset fonts. This is the same Best routine and
        # final writer as pipeline._save_optimized_pdf, without repeating it.
        selection = best.save_best_streams(doc, str(target), writer=study.pipeline._write_optimized_pdf,
                                           image_prediction="preserve",
                                            directory=str(folder), brotli_declaration=False, no_new_id=True)
    with study.fitz.open(target) as output:
        if semantic_graph(output) != expected_graph or study.streams.brotli_declaration_present(output):
            raise ValueError("Best save changed document semantics or declaration")
    selection.pop("encode_seconds", None)  # Size-only experiment, not a time benchmark.
    result = dict(stream_policy="best", brotli_declaration=False,
                  pdf=str(target), pdf_sha256=digest(target), complete_pdf_bytes=target.stat().st_size,
                  exact_semantic_graph=True, selection=selection,
                  render_proof=dict(source="frozen verified preparation", seed_pdf=seed["result"]["pdf"],
                                    exact_all_page_pixels=seed["result"]["exact_all_page_pixels"],
                                    semantic_graph_sha256=expected_graph))
    record = dict(identity=expected_identity, job=job, document=document.key, recipe=recipe.key, result=result)
    validate_measured(record)
    checkpoint.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(dict(document=document.key, recipe=recipe.key,
                          complete_pdf_bytes=result["complete_pdf_bytes"],
                          selected=selection["winner"])), flush=True)
    return record


def table(documents, recipes, records):
    by_key = {}
    for record in records:
        key = record["document"], record["recipe"]
        if key in by_key:
            raise ValueError(f"Duplicate Best measurement: {key}")
        result = record["result"]
        value = result["complete_pdf_bytes"]
        if result.get("stream_policy") != "best" or not result.get("exact_semantic_graph"):
            raise ValueError("Overview requires actual verified Best measurements")
        if type(value) is not int or value <= 0:
            raise ValueError("Overview requires positive measured integer bytes")
        by_key[key] = value
    minima = {}
    for recipe in recipes:
        for document in documents:
            key = document.key, recipe.key
            if key not in by_key:
                raise ValueError(f"Missing measured Best cell: {key}")
            group = document.key, recipe.family
            minima[group] = min(minima.get(group, by_key[key]), by_key[key])
    lines = ["| Algorithm combination | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|" * len(documents)]
    current = None
    for recipe in recipes:
        if recipe.section != current:
            current = recipe.section
            lines.append(f"| **{current}** |" + " |" * len(documents))
        cells = []
        for document in documents:
            size = by_key[document.key, recipe.key]
            cells.append(f"**{size:,}**" if size == minima[document.key, recipe.family] else f"{size:,}")
        lines.append("| " + recipe.label + " | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def binary_table(documents, recipes, publication):
    index = fixed_records(publication)
    lines = ["| Image recipe / reference | " + " | ".join(d.label for d in documents) + " |",
             "|---|" + "---:|" * len(documents)]
    current = None
    for recipe in recipes:
        if recipe.section != current:
            current = recipe.section
            lines.append(f"| **{current}** |" + " |" * len(documents))
        values = [overview.measured_effect_cell(*(r["result"]["complete_pdf_bytes"]
                  for r in fixed_pair(d, recipe, index)), show_size=False) for d in documents]
        lines.append("| " + recipe.label + " | " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def run(publication_path, folder, *, workers=2, resume=False):
    publication = load_publication(publication_path)
    expected_identity = identity(publication_path)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=resume)
    frozen = folder / "identity.json"
    if frozen.exists() and json.loads(frozen.read_text()) != expected_identity:
        raise ValueError("Changed Best study; use a new directory, not incompatible resume")
    frozen.write_text(json.dumps(expected_identity, indent=2) + "\n")
    index, results = fixed_records(publication), {}
    jobs = []
    for document in overview.DOCUMENTS:
        for recipe in RECIPES:
            baseline, seed = fixed_pair(document, recipe, index)
            # Fixed controls remain actual verified outputs, never renamed Best.
            for record in (baseline, seed):
                overview.validate_record(record["case"], record["result"])
            jobs.append((document, recipe, seed, folder / "jobs" / document.key / recipe.key))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        pending = {pool.submit(measure, *job, expected_identity, resume): (job[0].key, job[1].key)
                   for job in jobs}
        for future in as_completed(pending):
            key = pending[future]
            results[key] = future.result()
            (folder / "metrics.json").write_text(json.dumps(dict(identity=expected_identity,
                complete=len(results) == len(jobs), records=list(results.values())), indent=2) + "\n")
    records = [results[d.key, r.key] for d in overview.DOCUMENTS for r in RECIPES]
    (folder / "matrix.md").write_text(table(overview.DOCUMENTS, RECIPES, records))
    (folder / "binary.md").write_text(binary_table(overview.DOCUMENTS, RECIPES, publication))
    print(f"BEST OVERVIEW COMPLETE: {len(records)} actual verified PDFs", flush=True)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication", type=Path, default=PUBLICATION)
    parser.add_argument("--label", default="best-overview-300dpi-20261017")
    parser.add_argument("--workers", type=int, choices=(1, 2), default=2)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if Path(args.label).name != args.label or args.label in (".", ".."):
        parser.error("label must be one directory name")
    run(args.publication, Path(".tmp/compression-experiments") / args.label,
        workers=args.workers, resume=args.resume)


if __name__ == "__main__":
    main()
