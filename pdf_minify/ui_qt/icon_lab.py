"""Stock artwork comparison with stable, shareable choices (§200).

This design-review window never applies icons, edits settings or touches PDFs.
Family-specific resources bypass desktop-theme inheritance deliberately.
"""
import base64
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QColor, QIcon, QPalette, QPixmap
from PySide6.QtWidgets import (
    QApplication, QButtonGroup, QComboBox, QDialog, QDialogButtonBox, QFrame,
    QHBoxLayout, QHeaderView, QLabel, QPlainTextEdit, QPushButton, QRadioButton,
    QTableWidget, QToolButton, QVBoxLayout, QWidget,
)

from .icons import ASSET_ROOT as BREEZE_ROOT
from .layout import UI_PADDING

ASSET_ROOT = Path(__file__).resolve().parent / "assets" / "icon_lab"
FAMILIES = (("N", "Nuvola"), ("O", "Oxygen"), ("G", "GNOME Classic"), ("B", "Breeze"))


@dataclass(frozen=True)
class Action:
    key: str
    label: str
    size: int


ACTIONS = (
    Action("REV", "Revert Changes", 20),
    Action("REN", "Rename Filter", 20),
    Action("COP", "Save As / Copy", 20),
    Action("SAV", "Save Filter / PDF", 20),
    Action("STP", "Stop Export", 16),
    Action("ZIN", "Zoom In", 16),
    Action("ZOU", "Zoom Out", 16),
)


@dataclass(frozen=True)
class Candidate:
    family: str
    action: str
    variant: int
    name: str

    @property
    def code(self) -> str:
        return f"{self.family}-{self.action}-{self.variant:02d}"


# IDs are explicit, not generated from display order. Never reuse/reassign one.
CANDIDATES = (
    Candidate("N", "REV", 1, "document-revert"), Candidate("N", "REV", 2, "edit-undo"),
    Candidate("N", "REN", 1, "edit"),
    Candidate("N", "COP", 1, "edit-copy"), Candidate("N", "COP", 2, "document-save-as"),
    Candidate("N", "SAV", 1, "document-save"),
    Candidate("N", "STP", 1, "process-stop"), Candidate("N", "STP", 2, "dialog-cancel"),
    Candidate("N", "ZIN", 1, "zoom-in"), Candidate("N", "ZOU", 1, "zoom-out"),
    Candidate("O", "REV", 1, "document-revert"), Candidate("O", "REV", 2, "edit-undo"),
    Candidate("O", "REN", 1, "edit-rename"), Candidate("O", "REN", 2, "document-edit"),
    Candidate("O", "COP", 1, "edit-copy"), Candidate("O", "COP", 2, "document-save-as"),
    Candidate("O", "SAV", 1, "document-save"),
    Candidate("O", "STP", 1, "process-stop"), Candidate("O", "STP", 2, "dialog-cancel"),
    Candidate("O", "ZIN", 1, "zoom-in"), Candidate("O", "ZOU", 1, "zoom-out"),
    Candidate("G", "REV", 1, "document-revert"), Candidate("G", "REV", 2, "edit-undo"),
    Candidate("G", "REN", 1, "insert-text"),
    Candidate("G", "COP", 1, "edit-copy"), Candidate("G", "COP", 2, "document-save-as"),
    Candidate("G", "SAV", 1, "document-save"), Candidate("G", "STP", 1, "process-stop"),
    Candidate("G", "ZIN", 1, "zoom-in"), Candidate("G", "ZOU", 1, "zoom-out"),
    Candidate("B", "REV", 1, "document-revert"), Candidate("B", "REN", 1, "edit-rename"),
    Candidate("B", "COP", 1, "edit-copy"), Candidate("B", "SAV", 1, "document-save"),
    Candidate("B", "STP", 1, "process-stop"),
    Candidate("B", "ZIN", 1, "zoom-in"), Candidate("B", "ZOU", 1, "zoom-out"),
)
BY_CODE = {candidate.code: candidate for candidate in CANDIDATES}


@lru_cache(maxsize=1)
def resource_bank() -> dict:
    return json.loads((ASSET_ROOT / "resources.json").read_text(encoding="utf-8"))


def candidate_icon(candidate: Candidate, palette: QPalette, size: int) -> QIcon:
    """Load exactly this family, never a system theme's inherited substitute."""
    if candidate.family == "B":
        variant = "dark" if palette.color(QPalette.Button).lightnessF() < .5 else "light"
        grid = 16 if size <= 16 else 22
        source = BREEZE_ROOT / variant / str(grid) / f"{candidate.name}.svg"
        if not source.is_file():
            raise FileNotFoundError(f"Missing bundled Icon Lab asset: {source}")
        return QIcon(str(source))
    icon = QIcon()
    for source in resource_bank()[f"{candidate.family}/{candidate.name}"]:
        pixmap = QPixmap()
        if not pixmap.loadFromData(base64.b64decode(source["png"], validate=True), "PNG"):
            raise ValueError(f"Invalid bundled PNG: {candidate.code} / {source['size']}px")
        icon.addPixmap(pixmap)
    return icon


class IconLab(QDialog):
    """Compare, collect codes and copy; no production configuration mutation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Icon Lab — choose and share codes")
        self.setModal(False)
        self.resize(1040, 700)
        self.groups = {action.key: QButtonGroup(self) for action in ACTIONS}
        self.choices: dict[str, QRadioButton] = {}
        self.previews: dict[str, tuple[QToolButton, ...]] = {}
        self._desktop_palette = QPalette(self.palette())
        root = QVBoxLayout(self)
        root.setSpacing(UI_PADDING)
        intro = QLabel("Compare stock icons, choose per action, then copy the codes to share your choices. "
                       "Nothing is applied to the app.")
        intro.setWordWrap(True)
        root.addWidget(intro)
        controls = QHBoxLayout()
        controls.addWidget(QLabel("Background:"))
        self.background = QComboBox()
        self.background.addItems(["Desktop", "Light", "Dark"])
        controls.addWidget(self.background)
        controls.addWidget(QLabel("Previews: app size · disabled · 32px inspection"))
        controls.addStretch()
        root.addLayout(controls)
        self.table = QTableWidget(len(ACTIONS), len(FAMILIES))
        self.table.setHorizontalHeaderLabels([f"{name} ({key})" for key, name in FAMILIES])
        self.table.setVerticalHeaderLabels([action.label for action in ACTIONS])
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setMinimumSectionSize(178)
        root.addWidget(self.table, 1)
        for row, action in enumerate(ACTIONS):
            for column, (family, _) in enumerate(FAMILIES):
                cell = QWidget()
                layout = QVBoxLayout(cell)
                layout.setContentsMargins(UI_PADDING, UI_PADDING, UI_PADDING, UI_PADDING)
                layout.setSpacing(UI_PADDING)
                for candidate in CANDIDATES:
                    if candidate.action == action.key and candidate.family == family:
                        layout.addWidget(self._candidate_card(candidate, action.size))
                layout.addStretch()
                self.table.setCellWidget(row, column, cell)
            self.groups[action.key].buttonToggled.connect(self._selection_changed)
        self.table.resizeRowsToContents()
        self.summary = QPlainTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setPlaceholderText("No choices yet. Codes will appear here; selections are not applied.")
        self.summary.setMaximumHeight(84)
        self.summary.setAccessibleName("Selected icon choice codes")
        root.addWidget(self.summary)
        bottom = QHBoxLayout()
        self.copy_button = QPushButton("Copy choices")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_choices)
        bottom.addWidget(self.copy_button)
        self.clear_button = QPushButton("Clear choices")
        self.clear_button.setEnabled(False)
        self.clear_button.clicked.connect(self.clear_choices)
        bottom.addWidget(self.clear_button)
        bottom.addStretch()
        close = QDialogButtonBox(QDialogButtonBox.Close)
        close.rejected.connect(self.close)
        bottom.addWidget(close)
        root.addLayout(bottom)
        self.background.currentIndexChanged.connect(self._change_background)
        self._refresh_previews()

    def _candidate_card(self, candidate, size):
        card = QFrame()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        radio = QRadioButton(candidate.code)
        radio.setProperty("choiceCode", candidate.code)
        radio.setToolTip(f"{dict(FAMILIES)[candidate.family]} · {candidate.name}\n"
                         "Select this code for review only; nothing is applied.")
        self.groups[candidate.action].addButton(radio)
        self.choices[candidate.code] = radio
        layout.addWidget(radio)
        source_name = QLabel(candidate.name)
        source_name.setTextInteractionFlags(Qt.TextSelectableByMouse)
        source_name.setWordWrap(True)
        layout.addWidget(source_name)
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(UI_PADDING)
        previews = []
        for icon_size, disabled in ((size, False), (size, True), (32, False)):
            button = QToolButton()
            button.setIconSize(QSize(icon_size, icon_size))
            button.setEnabled(not disabled)
            button.setAccessibleName(f"{candidate.code} {icon_size}px {'disabled' if disabled else 'preview'}")
            button.setToolTip(f"{candidate.code} · {icon_size}px {'disabled' if disabled else 'preview'}")
            button.clicked.connect(lambda checked=False, choice=radio: choice.setChecked(True))
            row.addWidget(button)
            previews.append(button)
        row.addStretch()
        layout.addLayout(row)
        self.previews[candidate.code] = tuple(previews)
        return card

    def _refresh_previews(self):
        for candidate in CANDIDATES:
            buttons = self.previews[candidate.code]
            icon = candidate_icon(candidate, buttons[0].palette(), buttons[0].iconSize().width())
            for button in buttons:
                button.setIcon(icon)

    def _selection_changed(self, button, checked):
        if checked:
            self.summary.setPlainText(self.choice_text())
            self.copy_button.setEnabled(True)
            self.clear_button.setEnabled(True)

    def choice_text(self) -> str:
        selected = []
        for action in ACTIONS:
            button = self.groups[action.key].checkedButton()
            if button is not None:
                selected.append(f"{action.label}: {button.property('choiceCode')}")
        return "\n".join(selected)

    def copy_choices(self):
        text = self.choice_text()
        if text:
            QApplication.clipboard().setText(text)

    def clear_choices(self):
        for group in self.groups.values():
            group.setExclusive(False)
            for button in group.buttons():
                button.setChecked(False)
            group.setExclusive(True)
        self.summary.clear()
        self.copy_button.setEnabled(False)
        self.clear_button.setEnabled(False)

    def _change_background(self, index):
        palette = QPalette(self._desktop_palette)
        if index:
            dark = index == 2
            for role, light, dim in (
                    (QPalette.Window, "#eff0f1", "#232629"),
                    (QPalette.Button, "#eff0f1", "#31363b"),
                    (QPalette.Base, "#ffffff", "#1b1e20"),
                    (QPalette.AlternateBase, "#e5e7e9", "#292e32"),
                    (QPalette.Text, "#232629", "#fcfcfc"),
                    (QPalette.WindowText, "#232629", "#fcfcfc"),
                    (QPalette.ButtonText, "#232629", "#fcfcfc")):
                palette.setColor(role, QColor(dim if dark else light))
            for role in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
                palette.setColor(QPalette.Disabled, role, QColor("#80858a"))
        self.setPalette(palette)
        self._refresh_previews()
