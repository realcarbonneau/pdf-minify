"""Remove the parts of a bundled PySide6 that PDF Minify never loads.

Usage: python trim_pyside6.py PATH_TO_PySide6

The app uses QtCore, QtGui and QtWidgets on a desktop. The PySide6 wheels
also carry Qt's developer tools, headers, type stubs, QML, and plugins for
databases, printing, Qt Designer, embedded displays and a virtual keyboard.
Some of those plugins need libraries no target has, and PySide6's deployment
scripts include templates named .py that are not Python (compileall fails on
them). The same list serves every package: debian/rules (Ubuntu 24.04) and
the Windows and macOS builds. Paths that a platform does not have are skipped.
"""
import shutil
import sys
from pathlib import Path

TOOLS = ["assistant", "designer", "linguist", "lrelease", "lupdate", "qmlcachegen", "qmlformat",
         "qmlimportscanner", "qmllint", "qmlls", "qmltyperegistrar", "rcc", "svgtoqml", "uic"]
DEVELOPER = ["include", "typesystems", "doc", "glue", "scripts"]
QT_FOLDERS = ["qml", "metatypes", "libexec"]
PLUGIN_FOLDERS = ["sqldrivers", "printsupport", "designer", "qmltooling", "egldeviceintegrations"]
PLUGIN_FILES = ["imageformats/libqpdf.so", "platforminputcontexts/libqtvirtualkeyboardplugin.so",
                "platforms/libqeglfs.so", "platforms/libqlinuxfb.so", "platforms/libqminimalegl.so",
                "platforms/libqvkkhrdisplay.so", "platforms/libqvnc.so"]


def candidates():
    for tool in TOOLS:
        # Linux, Windows, macOS (the GUI tools are app bundles there).
        yield from (tool, tool + ".exe", tool.capitalize() + ".app")
    yield from DEVELOPER
    for name in QT_FOLDERS:
        yield from ("Qt/" + name, name)  # under Qt/ on Linux and macOS, at the top on Windows
    for name in PLUGIN_FOLDERS + PLUGIN_FILES:
        yield from ("Qt/plugins/" + name, "plugins/" + name)


def size(path):
    return path.stat().st_size if path.is_file() else sum(
        p.stat().st_size for p in path.rglob("*") if p.is_file() and not p.is_symlink())


def main(root):
    if not root.is_dir():
        print(f"{root}: no PySide6 here; nothing to trim")
        return
    freed = 0
    paths = [root / name for name in candidates()] + sorted(root.rglob("*.pyi"))
    for path in paths:
        if path.is_symlink() or path.is_file():
            freed += size(path)
            path.unlink()
        elif path.is_dir():
            freed += size(path)
            shutil.rmtree(path)
        else:
            continue
        print(f"removed {path.relative_to(root)}")
    print(f"PySide6 trimmed by {freed / 1e6:.0f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
