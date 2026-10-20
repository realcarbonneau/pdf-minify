"""Crop review sheets copy native pixels and pick distinct error tiles."""


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
