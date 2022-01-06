import mido
import time
from threading import Thread

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mido.backends.rtmidi import Output

    from .melody import Melody


class Carillon:
    """
    Klasse, die die Kommunikation zu GrandOrgue über MIDI-Messages abstrahiert
    zur Verfügung stellt.

    Attributes
    ----------
    port : Output
        MIDI-Port, an den die Nachrichten gesendet werden.
    priority : int
        Priorität der zuletzt gespielten Melodie. Sofern eine neue Melodie mit
        geringerer Priorität abgespielt werden soll, wird abgewiesen.
    thread : Thread
        Thread, der asynchron die Melodie abspielt.

    Methods
    -------
    play(melody, priority) : bool
        Spielt eine Melodie auf dem Carillon.
    stop()
        Bricht das Spielen der aktuellen Melodie ab.
    _threaded_play(melody)
        Eigentliche Abspielmethode, die zum Threaden genutzt wird.
    """
    def __init__(self, port: Output = None):
        """
        Erzeugt das Carillon und belegt es mit einem MIDI-Port vor.

        Parameters
        ----------
        port : mido.backends.rtmidi.Output (optional)
            MIDI-Port, der genutzt werden soll. Sofern keiner übergeben wird,
            wird ein Standardport geöffnet.
        """
        self.port = mido.open_output() if port is None else port
        self.priority: int = 0
        self.thread: Thread = None
        self.stopped: bool = False

    def play(self, melody: Melody, priority: int = 0) -> bool:
        """
        Spielt eine übergebene Melodie auf dem Carillon. Spielt bereits eine
        Melodie, wird erst überprüft, ob deren Priorität höher ist. In dem
        Falle wird abgewiesen.

        Parameters
        ----------
        melody : Melody
            Die abzuspielende Melodie.
        priorty : int
            Die Priorität, die der Melodie beigemessen wird. Nur wenn die
            Priorität mindestens genauso hoch ist wie die der gerade
            abgespielten Melodie wird diese abgebrochen und jene angefangen.

        Returns
        -------
        Wenn die Melodie gespielt wird `True`, ansonsten `False`. Dann spielte
        bereits eine Melodie mit höherer Priorität.
        """
        if self.thread and self.thread.is_alive():
            if self.priority > priority: return False
            self.stop()
        self.priority = priority
        self.thread = Thread(target=self._threaded_play, args=([melody]))
        self.thread.start()
        return True

    def stop(self) -> None:
        """Bricht die aktuell gespielte Melodie ab."""
        self.stopped = True
        self.thread.join()
        self.stopped = False
        self.port.reset()

    def _threaded_play(self, melody: Melody) -> None:
        """
        Interne Methode zum Abspielen der Melodie innerhalb eines Threads.

        Parameters
        ----------
        melody : Melody
            Abzuspielende Melodie.
        """
        for msg in melody.messages:
            if self.stopped: return
            time.sleep(msg.time)
            if self.stopped: return
            if not msg.is_meta: self.port.send(msg)
