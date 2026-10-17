"""Native concise help, with non-hover keyboard/accessibility equivalents."""


def set_control_help(widget, summary, details=""):
    """Keep native appearance/timing; help must never change application state."""
    widget.setToolTip(summary)
    widget.setAccessibleDescription(summary)
    widget.setWhatsThis(summary + ("\n\n" + details if details else ""))
