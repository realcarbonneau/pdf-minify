"""Stable-q matching selects decoded quality, never an imposed size saving."""

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from tools import bench_quality_match as bench


@pytest.mark.parametrize("q,rate", [(0,101),(5,96),(28,73),(53,48),(56,45),(69,32),(75,26),(77,24),(100,1)])
def test_fixed_conventional_q_scale_matches_reported_candidate(q, rate):
    assert bench.conventional_rate(q) == rate


@pytest.mark.parametrize("q", [True, -1, 101, 75.1, "75", None])
def test_invalid_q_is_not_normalized_or_silently_clamped(q):
    with pytest.raises(ValueError):
        bench.conventional_rate(q)


def test_search_matches_actual_quality_instead_of_wanted_bytes():
    seen=[]
    def evaluate(q):
        seen.append(q)
        # The closest point is intentionally larger than the JPEG reference
        # could be; byte savings must not override measured quality matching.
        return dict(ssimulacra2=q, bytes=10000+q)
    result=bench.search_integer_quality(evaluate,56.2)
    assert result["selected_q"]==56 and result["within_one_point"]
    assert result["selected"]["bytes"]==10056
    assert result["bracketed"] and len(seen)==len(set(seen))
    assert {55,56,57} <= set(result["measured_qs"])


@pytest.mark.parametrize("reference,q", [(-3,0),(103,100)])
def test_unattainable_endpoint_is_reported_not_claimed_matched(reference,q):
    result=bench.search_integer_quality(lambda x:dict(ssimulacra2=x,bytes=100+x),reference)
    assert result["selected_q"]==q
    assert not result["bracketed"] and not result["within_one_point"]


def test_measured_nonmonotonic_local_neighbour_is_considered():
    def evaluate(q):
        return dict(ssimulacra2=55.95 if q==57 else float(q), bytes=100+q)
    result=bench.search_integer_quality(evaluate,55.95)
    assert result["selected_q"]==57


@pytest.mark.parametrize("output", ["nan", "Score: nan", "Score: inf", "garbage", "Score: 50\nScore: 70"])
def test_metric_failures_cannot_be_replaced_by_assumed_scores(monkeypatch, output):
    monkeypatch.setattr(bench.subprocess,"run",lambda *a,**kw:SimpleNamespace(stdout=output))
    with pytest.raises(ValueError):
        bench.metric_score(Path("metric"),Path("source"),Path("decoded"))


def test_metric_preserves_valid_negative_score_and_pins_input_arguments(monkeypatch):
    def run(args,**kwargs):
        assert args==["metric","image","source","decoded"]
        assert kwargs["check"] and kwargs["env"]["RAYON_NUM_THREADS"]=="1"
        return SimpleNamespace(stdout="Score: -2.50000000\n")
    monkeypatch.setattr(bench.subprocess,"run",run)
    assert bench.metric_score(Path("metric"),Path("source"),Path("decoded"))==-2.5


def test_psnr_exact_case_has_explicit_null_not_nan_or_made_up_db():
    source=np.zeros((8,8,3),dtype=np.uint8)
    assert bench.psnr(source,source) is None
    assert bench.psnr(source,source+1)==pytest.approx(48.1308036087)


@pytest.mark.parametrize("q,target",[(0,1),(1,1),(34,34),(56,56),(75,75),(100,100)])
def test_alternative_convention_has_fixed_targets_not_jpeg_reference_normalization(q,target):
    from tools.bench_jpx_psnr_match import target_db
    assert target_db(q)==target


def test_alternative_uses_same_lossy_profile_and_only_changes_rate_control():
    from tools.bench_jpx_psnr_match import encode
    class Source:
        size=(64,96)
        def save(self,stream,format,**kwargs):
            assert format=="JPEG2000"
            assert kwargs==dict(quality_mode="dB",quality_layers=[35],irreversible=True,mct=1,
                               num_resolutions=6,codeblock_size=(64,64),progression="LRCP",tile_size=None)
            stream.write(b"measured backend output")
    assert encode(Source(),35)==b"measured backend output"
