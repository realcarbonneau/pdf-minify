"""Source-order ownership of flat page/panel fills, not image coverage masks."""

from dataclasses import dataclass

import pymupdf as fitz


@dataclass(frozen=True)
class BackdropFill:
    rect: tuple
    stroked: bool
    background: bool


@dataclass(frozen=True)
class BackdropPlan:
    fills: tuple = ()

    @classmethod
    def from_page(cls, page):
        images = [(seq, fitz.Rect(box)) for seq, (kind, box) in
                  enumerate(page.get_bboxlog()) if kind == "fill-image"]
        fills = []
        for drawing in page.get_drawings():
            items = drawing["items"]
            if (drawing["fill"] is None or len(items) != 1
                    or items[0][0] != "re"):
                continue
            rect = drawing["rect"]
            background = drawing["fill_opacity"] == 1 and (
                rect.contains(page.rect) or any(
                    seq > drawing["seqno"] and not image.is_empty
                    and rect.contains(image) for seq, image in images))
            # Retain non-background occurrences too: equal geometry is not
            # equal ownership (e.g. a panel followed by a translucent overlay).
            fills.append(BackdropFill(tuple(rect), "s" in drawing["type"], background))
        return cls(tuple(fills))

    def cursor(self):
        return _FillCursor(self.fills)


class _FillCursor:
    def __init__(self, fills):
        self.fills = fills
        self.used = set()

    def is_background(self, rect, *, stroked):
        for index, fill in enumerate(self.fills):
            if (index not in self.used and fill.stroked == stroked
                    and max(abs(a - b) for a, b in zip(rect, fill.rect)) < .01):
                self.used.add(index)
                return fill.background
        return False
