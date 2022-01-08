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

    Methods
    -------
    __add__(other) : Melody
        Fügt zwei Melodien zusammen.
    __iadd__(other) : Melody
        Fügt eine Melodie an.
    __mul__(other) : Melody
        Wiederholt eine Melodie mehrmals.
    __imul__(other) : Melody
        Wiederholt die Melodie inline mehrmals.
    __rmul__(other) : Melody
        Wiederholt eine Melodie mehrmals.

    Class Methods
    -------------
    from_file(path) : Melody
        Erzeugt eine Melodie aus einer MIDI-Datei.
    """

    def __init__(self, messages: List[mido.Message] = None):
        """
        Erstellt die Melodie aus den übergebenen Nachrichten.

        Parameters
        ----------
        messages : List[mido.Message] (optional)
            Nachrichten, die die Melodie ergeben.
        """
        self._messages = [] if messages is None else messages
        self.transpose: int = 0
        self.tempo: float = 1

    @property
    def messages(self) -> List[mido.Message]:
        """MIDI-Nachrichten mit Anpassung durch Tempo und Transponierung."""
        messages = [m.copy() for m in self._messages]
        for m in messages:
            m.time /= self.tempo
            if m.type in ('note_on', 'note_off'): m.note += self.transpose
        return messages

    def __add__(self, other: 'Melody') -> 'Melody':
        """
        Fügt zwei Melodien zu einer neuen Melodie zusammen. Dabei werden die
        Einstellungen zu Transponierung und Tempo beider Summanden angewendet.

        Parameters
        ----------
        other : Melody
            Melodie, die angehängt werden soll.

        Returns
        -------
        Zusammengefügte Melodie.
        """
        if not isinstance(other, Melody): return NotImplemented
        melody = Melody(self.messages + other.messages)
        melody.transpose = self.transpose
        melody.tempo = self.tempo
        return melody

    def __iadd__(self, other: 'Melody') -> 'Melody':
        """
        Fügt eine Melodie an die aktuelle an, ohne ein neues Objekt zu
        erstellen. Einstellungen zu Transponierung und Tempo bleiben erhalten.

        Parameters
        ----------
        other : Melody
            Melodie, die angehängt werden soll.

        Returns
        -------
        Das Objekt selbst.
        """
        if not isinstance(other, Melody): return NotImplemented
        self._messages += other.messages
        return self

    def __mul__(self, other: int) -> 'Melody':
        """
        Wiederholt eine Melodie und erzeugt ein neues Melodieobjekt.
        Einstellungen zu Transponierung und Tempo bleiben erhalten.

        Parameters
        ----------
        other : int
            Anzahl der Wiederholungen.

        Returns
        -------
        Neues Melodieobjekt, das entsprechend häufig wiederholt die Melodie
        enthält.
        """
        if not isinstance(other, int): return NotImplemented
        melody = Melody(self._messages * other)
        melody.transpose = self.transpose
        melody.tempo = self.tempo
        return melody

    def __imul__(self, other: int) -> 'Melody':
        """
        Wiederholt die Melodie inline, ohne ein neues Melodieobjekt zu
        erstellen. Einstellungen bleiben erhalten.

        Parameters
        ----------
        other : int
            Anzahl der Wiederholungen.

        Returns
        -------
        Das Objekt selbst.
        """
        if not isinstance(other, int): return NotImplemented
        self._messages *= other
        return self

    def __rmul__(self, other: int) -> 'Melody':
        """
        Wiederholt eine Melodie und erzeugt ein neues Melodieobjekt.
        Einstellungen zu Transponierung und Tempo bleiben erhalten. Erlaubt die
        Rechtsmultiplikation.

        Parameters
        ----------
        other : int
            Anzahl der Wiederholungen.

        Returns
        -------
        Neues Melodieobjekt, das entsprechend häufig wiederholt die Melodie
        enthält.
        """
        return self * other

    @classmethod
    def from_file(cls, path: str) -> 'Melody':
        """
        Factory-Methode, die eine Melodie aus einer MIDI-Datei extrahiert.

        Parameters
        ----------
        path : str
            Pfad zur MIDI-Datei.
        """
        return cls(list(mido.MidiFile(path)))
