import enum


class Season(enum.Enum):
    """Kodierung der liturgischen Zeit."""

    ORDINARY = enum.auto()
    CHRISTMAS = enum.auto()
    LENT = enum.auto()
    EASTER = enum.auto()
