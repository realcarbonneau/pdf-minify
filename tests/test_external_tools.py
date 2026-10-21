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


def test_tools_get_long_windows_paths_in_the_long_path_form(monkeypatch):
    """zopfli.exe could not open its 290-character scratch path (MAX_PATH 260)."""
    import ntpath
    monkeypatch.setattr(external_tools.os, "name", "nt")
    monkeypatch.setattr(external_tools.os, "path", ntpath)
    deep = "C:\\Users\\someone\\AppData\\Local\\Temp\\pdf-minify\\saves\\" + "x" * 250 + "\\stream"
    assert external_tools.tool_path(deep) == "\\\\?\\" + deep
    assert external_tools.tool_path("\\\\?\\" + deep) == "\\\\?\\" + deep  # once only
    short = "C:\\Temp\\stream"
    assert external_tools.tool_path(short) == short


def test_jbig2_input_stays_short_on_windows(monkeypatch):
    r"""jbig2 reads through Leptonica, which turns \\?\ into //?/ on Windows."""
    import ntpath
    monkeypatch.setattr(external_tools.os, "name", "nt")
    monkeypatch.setattr(external_tools.os, "path", ntpath)
    base = "C:\\Users\\someone\\AppData\\Local\\Temp\\pdf-minify\\saves\\"
    fits = base + "x" * (218 - len(base))  # + "\" + a 40-character name = 259
    assert external_tools.short_scratch_dir(fits) == fits
    assert external_tools.short_scratch_dir(fits + "x") is None  # the system temp folder
    assert external_tools.short_scratch_dir(None) is None


@pytest.mark.skipif(pipeline.jbig2_binary() is None, reason="no jbig2")
def test_jbig2_encodes_from_a_deep_scratch_folder(tmp_path):
    """The Windows filter tests failed here: a ~270-character scratch path."""
    import numpy as np
    deep = tmp_path
    while len(str(deep)) < 300:
        deep = deep / ("d" * 40)
    deep.mkdir(parents=True)
    bw = np.full((64, 96), 255, np.uint8)
    bw[16:48, 20:76] = 0
    token = pipeline._ENCODE_WORKDIR.set(str(deep))
    try:
        payload = pipeline.encode_binary_jbig2(bw)
    finally:
        pipeline._ENCODE_WORKDIR.reset(token)
    assert payload and pipeline.jbig2_renders(payload, 96, 64, bw)
    assert not list(deep.iterdir())  # its input is deleted
