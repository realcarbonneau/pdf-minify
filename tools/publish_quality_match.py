"""Audit LOSSY-04 real measurements and publish the research, not size estimates."""

import argparse
import io
import json
import math
from pathlib import Path

from PIL import Image
from tools import bench_quality_match as match
from tools import bench_jpx_psnr_match as psnr_match
from tools.publish_lossy_controls import patch_files

REPORT=Path("docs/JPEG_JPEG2000_RESEARCH.md")
FIXTURE=Path("tests/fixtures/jpeg_jpeg2000_quality_match.json")
SECTION="## Actual measured equivalence results"


def audit_preparations(rate_path):
    prepared_path=rate_path.parent/'preparations.json'
    data=json.loads(prepared_path.read_text())
    if not data.get('complete') or data['identity']['driver_sha256']!=match.file_digest(match.__file__):
        raise ValueError('Incomplete or changed original RGB preparation')
    for document in data['identity']['documents']:
        if match.file_digest(document['source'])!=document['sha256']:
            raise ValueError('Changed complete source PDF')
    baseline_proof=json.loads(Path('tests/fixtures/lossy_quality_sizes.json').read_text())
    baseline=Path(baseline_proof['measured_manifest'])
    if match.file_digest(baseline)!=baseline_proof['measured_manifest_sha256']:
        raise ValueError('Changed original LOSSY-02 proof')
    previous=json.loads(baseline.read_text())
    old={(r['document'],r['force_raster']):r for r in previous['records'] if r['mode']=='color'}
    index={}
    count=0
    for case in data['cases']:
        key=case['job']['document']['key'],case['job']['force_raster']
        if key in index or case['job']['identity']!=data['identity']:
            raise ValueError('Duplicate or changed producing preparation')
        index[key]=case
        if match.file_digest(case['reference_pdf'])!=case['reference_pdf_sha256']:
            raise ValueError('Altered actual reference PDF')
        expected=old[key]['canvases']
        if len(expected)!=len(case['canvases']):
            raise ValueError('Changed prepared canvas inventory')
        for a,b in zip(expected,case['canvases'],strict=True):
            match.verify_files([b])
            if ((a['width'],a['height'],a['samples_sha256'],a['payload_sha256'])!=
                    (b['width'],b['height'],b['samples_sha256'],b['jpeg_sha256'])):
                raise ValueError('Changed actual RGB samples or JPEG q75 reference')
            count+=1
    if set(index)!={(d.key,force) for d in match.DOCUMENTS for force in (False,True)} or count!=78:
        raise ValueError('Missing complete preparation case')
    return prepared_path,data,index


def audit(path,driver,scale):
    data=json.loads(path.read_text())
    identity=data["identity"]
    if (not data.get("complete") or data.get("first_canvas_only") is not True
            or identity["driver_sha256"]!=match.file_digest(driver.__file__)
            or identity["jpx_quality_scale"]!=scale
            or (scale==psnr_match.SCALE and identity.get('helper_sha256')!=match.file_digest(match.__file__))
            or identity["ssimulacra2_sha256"]!=match.file_digest(identity["ssimulacra2_binary"])):
        raise ValueError("Incomplete, changed or mis-scoped actual quality experiment")
    expected={(d.key,force,0) for d in match.DOCUMENTS for force in (False,True)}-{("native",False,0)}
    keys=[]
    rows=[]
    for result in data["records"]:
        row=result["job"]["canvas"]
        key=row['document'],row['force_raster'],row['canvas']
        keys.append(key)
        if result['job']['identity']!=identity or not result.get('complete'):
            raise ValueError("Changed producing job or incomplete quality result")
        if not math.isfinite(result['reference_score']):
            raise ValueError('Invalid measured reference score')
        match.verify_files([row])
        source=Image.open(row['source_png']).convert('RGB')
        if match.digest(source.tobytes())!=row['samples_sha256']:
            raise ValueError("Changed prepared RGB samples")
        jpeg=Image.open(row['jpeg']).convert('RGB')
        if jpeg.tobytes()!=Image.open(row['jpeg_decoded_png']).convert('RGB').tobytes():
            raise ValueError("Reference pixels do not decode from the real JPEG")
        actual_reference_psnr=match.psnr(source,jpeg)
        if actual_reference_psnr!=result['reference_psnr']:
            raise ValueError("Incorrect actual reference PSNR")
        for q,candidate in result['candidates'].items():
            if type(candidate['q']) is not int or str(candidate['q'])!=q:
                raise ValueError("Candidate mislabeled with a different q")
            target=match.conventional_rate(candidate['q']) if scale==match.SCALE else psnr_match.target_db(candidate['q'])
            if candidate['rate' if scale==match.SCALE else 'target_psnr']!=target:
                raise ValueError("Candidate uses a different quality scale")
            if not math.isfinite(candidate['ssimulacra2']):
                raise ValueError("Invalid perceptual score")
            for field in ('jp2','decoded_png'):
                if match.file_digest(candidate[field])!=candidate[field+'_sha256']:
                    raise ValueError("Altered measured candidate")
            if Path(candidate['jp2']).stat().st_size!=candidate['bytes']:
                raise ValueError("Incorrect actual image byte count")
        chosen=match.search_integer_quality(lambda q:result['candidates'][str(q)],result['reference_score'])
        if any(result[field]!=value for field,value in chosen.items()):
            raise ValueError("Selected q does not match the measured candidate search")
        selected=result['selected']
        raw=Image.open(io.BytesIO(Path(selected['jp2']).read_bytes())).convert('RGB')
        png=Image.open(selected['decoded_png']).convert('RGB')
        if raw.size!=source.size or raw.tobytes()!=png.tobytes() or match.psnr(source,raw)!=selected['psnr']:
            raise ValueError("Selected quality pixels do not decode from the actual JPEG2000")
        rows.append(dict(document=row['document'],force_raster=row['force_raster'],canvas=0,
                         width=row['width'],height=row['height'],source_samples_sha256=row['samples_sha256'],
                         jpeg_q=75,jpeg_score=result['reference_score'],jpeg_psnr=result['reference_psnr'],
                         jpeg_rgb_ratio=row['width']*row['height']*3/row['jpeg_bytes'],
                         jpeg_sha256=row['jpeg_sha256'],jpx_q=selected['q'],jpx_score=selected['ssimulacra2'],
                         jpx_psnr=selected['psnr'],jpx_sha256=selected['jp2_sha256'],
                         score_gap=selected['ssimulacra2']-result['reference_score'],
                         within_one_point=chosen['within_one_point'],bracketed=chosen['bracketed'],
                         measured_qs=chosen['measured_qs']))
    if len(keys)!=len(set(keys)) or set(keys)!=expected:
        raise ValueError("Missing, duplicate or unexpected image-bearing case")
    rows.sort(key=lambda r:(r['document'],r['force_raster']))
    return dict(quality_scale=scale,manifest=str(path),manifest_sha256=match.file_digest(path),rows=rows)


def make_fixture(rate_path,psnr_path):
    prepared_path,prepared,index=audit_preparations(rate_path)
    for path in (rate_path,psnr_path):
        data=json.loads(path.read_text())
        for result in data['records']:
            row=result['job']['canvas']
            if row!=index[row['document'],row['force_raster']]['canvases'][0]:
                raise ValueError('Quality result is bound to a different source or canvas')
        if path==psnr_path and (data['identity']['preparation_manifest']!=str(prepared_path)
                               or data['identity']['preparation_sha256']!=match.file_digest(prepared_path)):
            raise ValueError('PSNR-convention result uses a different RGB preparation')
    studies=[audit(rate_path,match,match.SCALE),audit(psnr_path,psnr_match,psnr_match.SCALE)]
    for a,b in zip(studies[0]['rows'],studies[1]['rows'],strict=True):
        if any(a[k]!=b[k] for k in ('document','force_raster','source_samples_sha256','jpeg_sha256','jpeg_score')):
            raise ValueError("Rate-control comparison changed the reference pixels or JPEG")
    rate=json.loads(rate_path.read_text())
    return dict(designer_rulings=[269,270],dpi=300,jpeg_q=75,
                scope='first encoded canvas per native/FFPR case; not all-page quality certification',
                cases=11,prepared_canvases=78,metric='SSIMULACRA2 Rust 0.5.0 / CLI 0.5.2',
                metric_binary_sha256=rate['identity']['ssimulacra2_sha256'],
                preparation_manifest_sha256=match.file_digest(prepared_path),studies=studies)


def result_table(study):
    labels={d.key:d.label for d in match.DOCUMENTS}
    setting='JPEG2000 target (dB)' if study.get('quality_scale')==psnr_match.SCALE else 'JPEG2000 actual q'
    lines=[f'| Case | JPEG q75 score | {setting} | JPEG2000 score | Score gap | Within 1 point? |',
           '|---|---:|---:|---:|---:|---|']
    for r in study['rows']:
        label=labels[r['document']]+(' · FFPR' if r['force_raster'] else ' · native')
        lines.append(f"| {label} | {r['jpeg_score']:.3f} | {r['jpx_q']} | {r['jpx_score']:.3f} | "
                     f"{r['score_gap']:+.3f} | {'Yes' if r['within_one_point'] else 'No — endpoint limit' if not r['bracketed'] else 'No — integer step'} |")
    return '\n'.join(lines)+'\n'


def markdown(proof):
    rate,psnr=proof['studies']
    matches=[sum(r['within_one_point'] for r in s['rows']) for s in proof['studies']]
    return (SECTION+'\n\n'
            '**Measured scope:** the first encoded RGB canvas in each of the eleven\n'
            'image-bearing native/FFPR cases, across all six representative PDFs.\n'
            'The no-image native W-9 has no bitmap-quality setting to match. All 78\n'
            'prepared RGB canvases and JPEG payloads were recovered and independently\n'
            'verified against LOSSY-02 hashes; these results do **not** claim that\n'
            'every page of every complete PDF has been quality-calibrated.\n\n'
            'JPEG is q75/4:4:4 in every row. Scores are measured from actual decoded\n'
            'images against their original prepared RGB; each JPEG2000 candidate\n'
            'receives those original pixels, never a JPEG-decoded intermediate.\n'
            'Positive gap means the metric favors JPEG2000. One point is the stated\n'
            'practical matching tolerance, not a human-observer equivalence claim.\n'
            'PSNR and source/payload hashes remain in the regression fixture.\n\n'
            f"### Previous darktable-based scale: {matches[0]} of 11 within one point\n\n"
            '`q = 101 − target ratio`; the scale is fixed, not JPEG-normalized.\n'
            'An endpoint-limit row cannot be called a matched-quality size test.\n'
            'A higher-quality result is not evidence of codec inefficiency; if it\n'
            'is also smaller it is conservative quality/size dominance, not an\n'
            'exactly equal-quality measurement.\n\n'
            f"For example, the artwork/native JPEG q75 reference achieves {rate['rows'][0]['jpeg_rgb_ratio']:.2f}:1\n"
            'against its raw RGB samples, beyond this scale\'s maximum 101:1 target.\n'
            'Large uniform page regions make a fixed raw-byte ratio especially\n'
            'unsuitable as a content-independent visual-quality control.\n\n'+result_table(rate)+'\n'
            f"### PSNR-target diagnostic: {matches[1]} of 11 within one point\n\n"
            'Here each setting is an OpenJPEG target in dB under the documented\n'
            'ImageMagick interior-value convention, with the explicit research\n'
            'endpoints described above. This is **not the previous scale or the\n'
            'current app quality scale**. Scores, not equality of PSNR, select the target.\n'
            'No saved-filter migration or runtime dependency is implied.\n\n'+result_table(psnr)+'\n'
            'Neither study establishes one universal JPEG2000 q56 for JPEG q75.\n'
            'The fixed-ratio scale has a demonstrated range problem; the second\n'
            'convention is a tested alternative, not a silent redefinition.\n'
            f"Its measured target settings span {min(r['jpx_q'] for r in psnr['rows'])}–{max(r['jpx_q'] for r in psnr['rows'])} dB;\n"
            'that is a content-dependent research diagnostic, not app q values.\n'
            'Under §271 these per-image fits are NOT experimental settings.\n'
            'Every current size experiment uses one fixed JPEG q75/JPX q75\n'
            'pair, with JPX targeting 26:1 on every canvas (LOSSY-05).\n'
            'Do not relabel the existing normalized-q75 PDF sizes as these results.\n\n'
            '### Provenance and reproduction\n\n'
            f"Metric binary SHA-256: `{proof['metric_binary_sha256']}`. "
            'The research-only Rust CLI is 0.5.2, library 0.5.0, with video/AVIF\n'
            'features disabled. The identity comparison returns exactly 100;\n'
            'this is a sanity check, not cross-implementation reader certification.\n\n'
            +''.join(f"- `{s['manifest']}` — SHA-256 `{s['manifest_sha256']}`.\n" for s in proof['studies'])+
            '\n`tests/fixtures/jpeg_jpeg2000_quality_match.json` pins the selected\n'
            'actual settings, both scores/PSNRs, complete source and payload hashes,\n'
            'scope and measured search points. Publication rechecks actual decoded\n'
            'JPEG/JP2 samples and the candidate selection without re-encoding or\n'
            'rerunning the metric. Raw transcripts and downloaded papers remain\n'
            'outside Git. No complete-PDF size estimate is published here.\n\n'
            '```sh\n'
            'nice -n 10 .venv/bin/python tools/bench_quality_match.py --output .tmp/jpeg-jpx-research/<rate-label> --metric <ssimulacra2_rs> --workers 2 --first-canvas-only\n'
            'nice -n 10 .venv/bin/python tools/bench_jpx_psnr_match.py --prepared .tmp/jpeg-jpx-research/<rate-label>/preparations.json --output .tmp/jpeg-jpx-research/<psnr-label> --metric <ssimulacra2_rs> --workers 2\n'
            '.venv/bin/python -m tools.publish_quality_match --rate .tmp/jpeg-jpx-research/<rate-label>/matches.json --psnr .tmp/jpeg-jpx-research/<psnr-label>/matches.json\n'
            '```\n\n'
            'Use `--resume` only with an unchanged producing identity. The first\n'
            'runner can extend to every prepared canvas without the first-only\n'
            'flag; the second uses `--all-canvases`. An extended study needs its\n'
            'actual larger scope published separately, not relabeled as this one.\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rate',type=Path,required=True)
    parser.add_argument('--psnr',type=Path,required=True)
    args=parser.parse_args()
    proof=make_fixture(args.rate,args.psnr)
    before=REPORT.read_text()
    if before.count(SECTION)!=1:
        raise ValueError('Changed research report structure')
    after=before.split(SECTION)[0]+markdown(proof)
    print(patch_files({FIXTURE:json.dumps(proof,indent=2)+'\n',REPORT:after}),end='')


if __name__=='__main__':
    main()
