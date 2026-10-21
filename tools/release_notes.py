#!/usr/bin/env python3
"""Print a release's section of CHANGELOG.md, the text of its GitHub
release page (docs/PACKAGING.md#release-notes), as Task Coach does.

    python3 tools/release_notes.py v0.0.1

Stops with an error when the section is missing or empty."""

import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parents[1] / "CHANGELOG.md"


def section(text, version):
    """The text under the version's heading, up to the next one; None
    when there is none."""
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## " + version:
            body = []
            for line in lines[index + 1:]:
                if line.startswith("## "):
                    break
                body.append(line)
            return "\n".join(body).strip() or None
    return None


def main(tag):
    version = tag.removeprefix("v")
    notes = section(CHANGELOG.read_text(encoding="utf-8"), version)
    if notes is None:
        sys.exit(f"CHANGELOG.md has no section for {version}")
    print(notes)


if __name__ == "__main__":
    main(sys.argv[1])
