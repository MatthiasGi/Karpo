from datetime import date
from typing import Any, Dict, List, Tuple

from .melody import Melody
from .settings import Settings
from .striker import Striker


class FestivePlayer:
    """
    Ermöglicht es, an festen Tagen zu beliebigen Uhrzeiten eine Melodie zu
    spielen. Damit können besondere Tage hervorgehoben werden.

    Attributes
    ----------
    festives : Dict[Tuple[int, int], List[Dict[str, Any]]]
        Dictionary, das jedem (Tag, Monat) aus den Einstellungen eine Liste mit
        Festen zuordnet.

    Methods
    -------
    _festive_play(melody, hours, quarters) : Melody
        Internes Callback, um die Melodie zu injizieren.
    """

    def __init__(self, striker: Striker):
        """
        Fügt dem Striker ein Callback hinzu, um bei Bedarf Melodien einzufügen.
        Dafür werden die Einstellungen analysiert und in eine performantere
        Form gebracht.

        Parameters
        ----------
        striker : Striker
            Schlagwerk, an das sich der Player hängen soll.
        """
        striker.subscribe(self._festive_play)
        data = list(Settings().festive.festives.values())
        self.festives: Dict[Tuple[int, int], List[Dict[str, Any]]] = \
            {(d['day'], d['month']): list() for d in data}
        for d in data: self.festives[(d['day'], d['month'])].append(d)

    def _festive_play(
        self, melody: Melody, hours: int, quarters: int
    ) -> Melody:
        """Callback, das bei bestimmten Festen eine Melodie anhängt."""
        today = (date.today().day, date.today().month)
        if today not in self.festives: return melody

        for d in self.festives[today]:
            h, q = d['time'].split(':')
            if hours != int(h) or quarters != int(q) // 15: return melody

            song = Melody.from_file(d['melody'])
            song.transpose = d.get('transpose', 0)
            song.tempo = d.get('tempo', 1)
            return melody + song
