"""LOSSY-04 alternative: a documented PSNR-based numeric JPEG2000 convention.

Research-only rate-control experiment; same prepared samples and lossy
Pillow/OpenJPEG profile. No app/recipe migration or replacement PDF writer.
"""

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image
from tools import bench_quality_match as match

SCALE="imagemagick-psnr-interior-v1"


def target_db(q):
    if type(q) is not int or not 0<=q<=100:
        raise ValueError("Expected integer q in 0..100")
    return max(1,q)


def encode(source,q):
    buf=io.BytesIO()
    source.save(buf,"JPEG2000",quality_mode="dB",quality_layers=[target_db(q)],
                irreversible=True,mct=1,num_resolutions=min(6,min(source.size).bit_length()),
                codeblock_size=(64,64),progression="LRCP",tile_size=None)
    return buf.getvalue()


def measure(row,folder,identity):
    match.verify_files([row])
    folder.mkdir(parents=True,exist_ok=True)
    checkpoint=folder/"quality-match.json"
    job=dict(identity=identity,canvas=row)
    if checkpoint.exists():
        result=json.loads(checkpoint.read_text())
        if result["job"]!=job:
            raise ValueError("Changed PSNR-convention matching identity")
    else:
        result=dict(job=job,complete=False,candidates={})
    source=Image.open(row["source_png"]).convert("RGB")
    if match.digest(source.tobytes())!=row["samples_sha256"]:
        raise ValueError("Changed original RGB samples")
    metric=Path(identity["ssimulacra2_binary"])
    if "reference_score" not in result:
        result["reference_score"]=match.metric_score(metric,row["source_png"],row["jpeg_decoded_png"])
        result["reference_psnr"]=match.psnr(source,Image.open(row["jpeg_decoded_png"]).convert("RGB"))
        match.write_json(checkpoint,result)

    def evaluate(q):
        old=result["candidates"].get(str(q))
        if old:
            for field in ("jp2","decoded_png"):
                if match.file_digest(old[field])!=old[field+"_sha256"]:
                    raise ValueError("Changed actual measured PSNR-convention candidate")
            return old
        data=encode(source,q)
        jp2,decoded=folder/f"q{q:03d}.jp2",folder/f"q{q:03d}-decoded.png"
        jp2.write_bytes(data)
        rgb=Image.open(io.BytesIO(data)).convert("RGB")
        if rgb.size!=source.size:
            raise ValueError("PSNR control changed source dimensions")
        rgb.save(decoded)
        measured=dict(q=q,target_psnr=target_db(q),bytes=len(data),jp2=str(jp2),
                      jp2_sha256=match.digest(data),decoded_png=str(decoded),
                      decoded_png_sha256=match.file_digest(decoded),psnr=match.psnr(source,rgb),
                      ssimulacra2=match.metric_score(metric,row["source_png"],decoded))
        result["candidates"][str(q)]=measured
        match.write_json(checkpoint,result)
        return measured

    chosen=match.search_integer_quality(evaluate,result["reference_score"])
    result.update(chosen,complete=True)
    match.write_json(checkpoint,result)
    print(f"PSNR-Q MATCH {row['document']} {'FFPR' if row['force_raster'] else 'native'}: "
          f"q{chosen['selected_q']}, SSIMULACRA2 gap "
          f"{chosen['selected']['ssimulacra2']-result['reference_score']:+.3f}",flush=True)
    return result


def run(prepared,folder,metric,workers=2,first=True,resume=False):
    original=json.loads(prepared.read_text())
    if not original.get("complete"):
        raise ValueError("Incomplete RGB preparations")
    identity=dict(original["identity"],study="LOSSY-04-psnr-convention-v1",jpx_quality_scale=SCALE,
                  producing_pipeline=match.overview.study.environment(),
                  preparation_manifest=str(prepared),preparation_sha256=match.file_digest(prepared),
                  ssimulacra2_binary=str(metric),ssimulacra2_sha256=match.file_digest(metric),
                  driver_sha256=match.file_digest(__file__),helper_sha256=match.file_digest(match.__file__))
    folder.mkdir(parents=True,exist_ok=resume)
    frozen=folder/"identity.json"
    if frozen.exists() and json.loads(frozen.read_text())!=identity:
        raise ValueError("Changed PSNR-convention study identity")
    match.write_json(frozen,identity)
    rows=[row for case in original["cases"] for row in (case["canvases"][:1] if first else case["canvases"])]
    if not 1<=workers<=2:
        raise ValueError("Use one or two bounded workers")
    results=[]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(measure,row,folder/row["document"]/('ffpr' if row['force_raster'] else 'native')/
                             f"canvas-{row['canvas']:02d}",identity) for row in rows]
        for future in as_completed(futures):
            results.append(future.result())
            match.write_json(folder/"matches.json",dict(identity=identity,complete=False,first_canvas_only=first,records=results))
    results.sort(key=lambda r:(r['job']['canvas']['document'],r['job']['canvas']['force_raster'],r['job']['canvas']['canvas']))
    match.write_json(folder/"matches.json",dict(identity=identity,complete=True,first_canvas_only=first,records=results))
    print(f"PSNR-Q COMPLETE: {len(results)} actual canvas matches; "
          f"{sum(r['within_one_point'] for r in results)} within one perceptual point",flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--metric',type=Path,required=True)
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--all-canvases',action='store_true')
    args=parser.parse_args()
    run(args.prepared,args.output,args.metric,args.workers,not args.all_canvases,args.resume)


if __name__=='__main__':
    main()
