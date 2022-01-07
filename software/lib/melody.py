import mido
from typing import List


class Melody:
    """
    Wrapper für eine Ansammlung an MIDI-Tönen, also eine Melodie. Die Herkunft
    der MIDI-Daten wird dadurch abstrahiert.

    Attributes
    ----------
    messages : List[mido.Message]
        Liste an MIDI-Nachrichten, die diese Melodie enthält, dabei wurden alle
        Einstellungen bereits angewendet.
    tempo : float
        Multiplikator für das Wiedergabetempo.
    transpose : int
        Anzahl der Halbtöne, um die transponiert werden soll.
    _messages : List[mido.Message]
        Interner Speicher für die unbearbeiteten MIDI-Nachrichten.

    Static Methods
    --------------
    from_file(path) : Melody
        Erzeugt eine Melodie aus einer MIDI-Datei.
    """

    def __init__(self, messages: List[mido.Message]):
        """
        Erstellt die Melodie aus den übergebenen Nachrichten.

        Parameters
        ----------
        messages : List[mido.Message]
            Nachrichten, die die Melodie ergeben.
        """
        self._messages = messages
        self.transpose: int = 0
        self.tempo: float = 1

    @property
    def messages(self) -> List[mido.Message]:
        """MIDI-Nachrichten mit Anpassung durch Tempo und Transponierung."""
        messages = [m.copy() for m in self._messages]
        for m in messages:
            m.time /= self.tempo
            if m.type not in ('note_on', 'note_off'): continue
            m.note += self.transpose
        return messages

    def from_file(path: str) -> 'Melody':
        """
        Factory-Methode, die eine Melodie aus einer MIDI-Datei extrahiert.

        Parameters
        ----------
        path : str
            Pfad zur MIDI-Datei.
        """
        return Melody(list(mido.MidiFile(path)))
