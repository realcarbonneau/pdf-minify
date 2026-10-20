"""Research scope, q conventions and measured equivalence stay explicit."""

import json
from pathlib import Path

import pytest

from tools import publish_quality_match as publication


def test_actual_published_research_matches_pinned_measurements():
    proof=json.loads(publication.FIXTURE.read_text())
    assert proof['designer_rulings']==[269,270]
    assert proof['cases']==11 and proof['prepared_canvases']==78
    assert proof['jpeg_q']==75 and proof['dpi']==300
    assert len(proof['metric_binary_sha256'])==64
    assert len(proof['preparation_manifest_sha256'])==64
    assert [s['quality_scale'] for s in proof['studies']]==[
        publication.match.SCALE,publication.psnr_match.SCALE]
    for study in proof['studies']:
        assert len(study['manifest_sha256'])==64
        assert len(study['rows'])==11
        assert len({(r['document'],r['force_raster']) for r in study['rows']})==11
        for row in study['rows']:
            assert row['jpeg_q']==75 and type(row['jpx_q']) is int
            assert row['jpeg_rgb_ratio']>0
            assert 0<=row['jpx_q']<=100
            assert row['score_gap']==row['jpx_score']-row['jpeg_score']
            assert row['within_one_point']==(abs(row['score_gap'])<=1)
            assert row['jpx_q'] in row['measured_qs']
            assert all(len(row[field])==64 for field in ('source_samples_sha256','jpeg_sha256','jpx_sha256'))
    before=publication.REPORT.read_text().split(publication.SECTION)[1]
    assert publication.SECTION+before==publication.markdown(proof)
    assert 'not all-page quality certification' in proof['scope']


def test_both_conventions_use_identical_source_and_jpeg_references():
    a,b=json.loads(publication.FIXTURE.read_text())['studies']
    for left,right in zip(a['rows'],b['rows'],strict=True):
        for field in ('document','force_raster','canvas','width','height','source_samples_sha256',
                      'jpeg_sha256','jpeg_score','jpeg_psnr'):
            assert left[field]==right[field]


def test_psnr_diagnostics_are_not_labeled_as_app_quality_or_benchmark_settings():
    proof=json.loads(publication.FIXTURE.read_text())
    rate,psnr=proof['studies']
    assert 'JPEG2000 actual q' in publication.result_table(rate)
    assert 'JPEG2000 target (dB)' in publication.result_table(psnr)
    assert 'JPEG2000 actual q' not in publication.result_table(psnr)
    assert 'per-image fits are NOT experimental settings' in publication.markdown(proof)


@pytest.mark.parametrize('complete,scope,scale',[(False,True,'darktable-rate-v1'),
                                               (True,False,'darktable-rate-v1'),
                                               (True,True,'incorrect-normalized-scale')])
def test_publisher_rejects_incomplete_or_mislabeled_experiments(tmp_path,complete,scope,scale):
    manifest=tmp_path/'matches.json'
    manifest.write_text(json.dumps(dict(complete=complete,first_canvas_only=scope,
                                      identity=dict(driver_sha256=publication.match.file_digest(publication.match.__file__),
                                                    jpx_quality_scale=scale))))
    with pytest.raises(ValueError):
        publication.audit(manifest,publication.match,publication.match.SCALE)


def test_publisher_rejects_changed_alternative_parameter_helper(tmp_path):
    manifest=tmp_path/'matches.json'
    manifest.write_text(json.dumps(dict(complete=True,first_canvas_only=True,
        identity=dict(driver_sha256=publication.match.file_digest(publication.psnr_match.__file__),
                      jpx_quality_scale=publication.psnr_match.SCALE,helper_sha256='changed'))))
    with pytest.raises(ValueError,match='changed'):
        publication.audit(manifest,publication.psnr_match,publication.psnr_match.SCALE)


def test_publisher_rejects_nonfinite_reference_score_before_selecting_quality(tmp_path):
    metric=tmp_path/'metric';metric.write_bytes(b'identity-only fixture; never executed')
    identity=dict(driver_sha256=publication.match.file_digest(publication.match.__file__),
                  jpx_quality_scale=publication.match.SCALE,ssimulacra2_binary=str(metric),
                  ssimulacra2_sha256=publication.match.file_digest(metric))
    row=dict(document='art',force_raster=False,canvas=0)
    manifest=tmp_path/'matches.json'
    manifest.write_text(json.dumps(dict(complete=True,first_canvas_only=True,identity=identity,
        records=[dict(complete=True,job=dict(identity=identity,canvas=row),reference_score=float('nan'))])))
    with pytest.raises(ValueError,match='reference score'):
        publication.audit(manifest,publication.match,publication.match.SCALE)


def test_research_preserves_the_prior_studies_and_distinguishes_qfactor():
    research=publication.REPORT.read_text()
    assert all(year in research for year in ('2000','2001','2003','2007'))
    assert '53%' in research and '11%' in research
    assert '317×476' in research
    assert 'Qfactor v2' in research
    assert '**not** a raw PSNR target' in research
    assert 'not a verified fixed JPEG2000 q equivalent' in research
    assert 'Source' not in publication.result_table(dict(rows=[]))  # no invented image-size estimates


def test_review_selects_both_error_types_and_distinct_original_tiles():
    import numpy as np
    from PIL import Image
    from tools.review_quality_match import crop_positions
    original=np.zeros((32,32,3),dtype=np.uint8)
    jpeg=original.copy();jpeg[:16,:16]=255
    jpx=original.copy();jpx[:16,16:]=255
    positions=crop_positions(*[Image.fromarray(x) for x in (original,jpeg,jpx)],side=16)
    assert positions[:2]==[(0,0),(16,0)]
    assert len(positions)==len(set(positions))==3


def test_review_pastes_native_pixels_without_resizing_or_filtering(tmp_path):
    import numpy as np
    from PIL import Image
    from tools.review_quality_match import render_case
    data=np.random.default_rng(4).integers(0,256,(512,512,3),dtype=np.uint8)
    path=tmp_path/'original.png';Image.fromarray(data).save(path)
    row=dict(source_png=str(path),jpeg_decoded_png=str(path),document='tiny',force_raster=False)
    record=dict(job=dict(canvas=row),complete=True,selected_q=56,selected=dict(decoded_png=str(path)))
    target=tmp_path/'review.png'
    proof=render_case(record,record,target)
    actual=np.asarray(Image.open(target))
    for i,(x,y) in enumerate(proof['positions']):
        yy=12+i*300+32
        for j in range(4):
            xx=12+j*268
            assert np.array_equal(actual[yy:yy+256,xx:xx+256],data[y:y+256,x:x+256])
