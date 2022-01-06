import mido
from typing import List

class Melody:
    """
    Wrapper für eine Ansammlung an MIDI-Tönen, also eine Melodie. Die Herkunft
    der MIDI-Daten wird dadurch abstrahiert.

    Attributes
    ----------
    messages : List[mido.Message]
        Liste an MIDI-Nachrichten, die diese Melodie enthält.

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
        self.messages = messages

    def from_file(path: str) -> 'Melody':
        """
        Factory-Methode, die eine Melodie aus einer MIDI-Datei extrahiert.

        Parameters
        ----------
        path : str
            Pfad zur MIDI-Datei.
        """
        return Melody(list(mido.MidiFile(path)))
