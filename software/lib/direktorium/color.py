import enum


class Color(enum.Enum):
    """Kodierung einer liturgischen Farbe."""

    NONE = enum.auto()
    WHITE = enum.auto()
    RED = enum.auto()
    GREEN = enum.auto()
    VIOLET = enum.auto()

    @staticmethod
    def parse(color: str) -> 'Color':
        """Interpretiert die liturgische Farbe aus der API."""
        if color == 'w': return Color.WHITE
        if color == 'r': return Color.RED
        if color == 'g': return Color.GREEN
        if color == 'v': return Color.VIOLET
        if color == '': return Color.NONE
        return None

    def __str__(self) -> str:
        if self is Color.WHITE: return 'Weiß'
        if self is Color.RED: return 'Rot'
        if self is Color.GREEN: return 'Grün'
        if self is Color.VIOLET: return 'Violett'
        if self is Color.NONE: return 'Keine Farbe'
        return 'Ungültige Farbe'
