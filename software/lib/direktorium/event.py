from dataclasses import dataclass
from datetime import date

from .color import Color
from .rank import Rank


@dataclass
class Event:
    """Klasse, die Informationen über ein Fest sammelt und zusammenfasst."""

    title: str
    date: date
    comment: str = ''
    lecture1: str = ''
    psalm: str = ''
    lecture2: str = ''
    gospel: str = ''
    color: Color = Color.NONE
    importance: int = 0
    rank: Rank = Rank.NONE

    @staticmethod
    def parse(data: dict) -> 'Event':
        """Interpretiert ein Fest aus der API."""
        return Event(
            title=data['Tl'],
            date=date.fromisoformat(data['Datum']),
            comment=data['Bem'],
            lecture1=data['L1'],
            psalm=data['AP'],
            lecture2=data['L2'],
            gospel=data['EV'],
            color=Color.parse(data['Farbe']),
            importance=data['Grad'],
            rank=Rank.parse(data['Rang']),
        )
