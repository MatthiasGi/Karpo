from typing import List, Tuple

from .melody import Melody
from .settings import AngelusSettings, Settings
from .striker import Striker


class AngelusPlayer:
    """
    Einfache Klasse, die zu in den Einstellungen festgelegten Zeiten eine
    Angelus-Melodie einspielen kann.

    Attributes
    ----------
    settings : AngelusSettings
        Einstellungsobjekt mit Anpassungen für den Angelus.
    times : List[Tuple[int, int]]
        Liste der Zeiten, zu denen ein Angelus spielen soll.

    Methods
    -------
    _play_angelus(melody, hours, quarters) : Melody
        Internes Callback zur Überprüfung und ggf. Durchführung des Abspielens.
    """

    def __init__(self, striker: Striker):
        """
        Registriert die Methode zum Abspielen des Angelus beim Schlagwerk.

        Parameters
        ----------
        striker : Striker
            Schlagwerk, das aufgemöbelt werden soll.
        """
        self.settings: AngelusSettings = Settings().angelus
        if self.settings.times is not None:
            striker.subscribe(self._play_angelus)

    @property
    def times(self) -> List[Tuple[int, int]]:
        """
        Liste aller Zeiten, zu denen ein Angelus spielen soll in Tupel-Form
        (Stunde, volle Viertelstunde).
        """
        if self.settings.times is None: return []
        times = []
        for t in self.settings.times.split(','):
            h, q = t.split(':')
            times.append((int(h), int(q) // 15))
        return times

    def _play_angelus(
        self, melody: Melody, hours: int, quarters: int
    ) -> Melody:
        """Callback zum ggf. nötigen Abspielen des Angelus."""
        if melody is None: return None
        if (hours, quarters) not in self.times: return melody
        angelus = Melody.from_file(self.settings.path)
        angelus.transpose = self.settings.transpose
        angelus.tempo = self.settings.tempo
        return melody + angelus
