from enum import IntEnum


class Rank(IntEnum):
    """Kodierung des Rangs eines Tages."""

    NONE = 0
    NICHTGEBOTEN = 1
    GEBOTEN = 2
    FEST = 3
    HOCHFEST = 4

    @staticmethod
    def parse(rank: str) -> 'Rank':
        """Interpretiert den Rang aus der API."""
        if rank == 'H': return Rank.HOCHFEST
        if rank == 'F': return Rank.FEST
        if rank == 'G': return Rank.GEBOTEN
        if rank == 'g': return Rank.NICHTGEBOTEN
        if rank == '': return Rank.NONE
        return None

    def __str__(self) -> str:
        if self is Rank.HOCHFEST: return 'Hochfest'
        if self is Rank.FEST: return 'Fest'
        if self is Rank.GEBOTEN: return 'Gebotener Gedenktag'
        if self is Rank.NICHTGEBOTEN: return 'Nichtgebotener Gedenktag'
        if self is Rank.NONE: return ''
        return 'Ungültiger Rang'
