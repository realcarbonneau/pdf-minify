"""The app runs its own copy of an encoder first, else the system's (PACKAGING.md)."""

import os
import stat

import pytest

from pdf_minify.core import external_tools, pipeline, stream_compression


def _fake_tool(directory, name):
    path = directory / (name + (".exe" if os.name == "nt" else ""))
    path.write_bytes(b"#!/bin/sh\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_bundled_copy_wins_over_the_system(tmp_path, monkeypatch):
    bundled = _fake_tool(tmp_path, "jbig2")
    monkeypatch.setattr(external_tools, "BUNDLED_BIN", tmp_path)
    monkeypatch.setattr(external_tools.shutil, "which",
                        lambda name, path=None, _which=external_tools.shutil.which:
                        _which(name, path=path) if path else "/usr/bin/" + name)
    # Windows reports the extension as PATHEXT spells it (jbig2.EXE).
    same = lambda found: os.path.normcase(found) == os.path.normcase(str(bundled))
    assert same(external_tools.find_tool("jbig2"))
    assert same(pipeline.jbig2_binary())
    # Not bundled: the system's.
    assert external_tools.find_tool("zopfli") == "/usr/bin/zopfli"
    assert pipeline.zopfli_binary() == "/usr/bin/zopfli"


def test_without_a_bin_folder_the_system_copy_is_used(tmp_path, monkeypatch):
    monkeypatch.setattr(external_tools, "BUNDLED_BIN", tmp_path / "missing")
    monkeypatch.setattr(external_tools.shutil, "which", lambda name, path=None: None)
    assert external_tools.find_tool("zopfli") is None
    assert stream_compression.find_tool is external_tools.find_tool


@pytest.mark.skipif(os.name == "nt", reason="the stand-in encoder is a #! script")
def test_deflate_best_runs_the_zopfli_it_found(tmp_path, monkeypatch):
    """A bundled zopfli is not on PATH: the encoder must run the found path."""
    import sys
    import zlib
    fake = tmp_path / "zopfli-elsewhere"
    # Stands in for zopfli: zlib level 1, so its output is recognisably its own.
    fake.write_text(f"#!{sys.executable}\nimport sys, zlib\n"
                    "sys.stdout.buffer.write(zlib.compress(open(sys.argv[-1], 'rb').read(), 1))\n")
    fake.chmod(0o755)
    monkeypatch.setattr(pipeline, "zopfli_binary", lambda: str(fake))
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    data = bytes(range(256)) * 64
    assert pipeline.deflate_best(data) == zlib.compress(data, 1) != zlib.compress(data, 9)
