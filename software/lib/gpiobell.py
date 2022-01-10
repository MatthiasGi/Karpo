from importlib import import_module
from threading import Thread
import time

from .carillon import Carillon
from .melody import Melody
from .mqttclient import MqttClient
from .settings import BellSettings, Settings

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import board
    import digitalio


class GpioBell:
    """
    Klasse, die für die Verwendung im RaspberryPi geeignet ist, um auf
    Knopfdruck (etwa eine Klingel) zu reagieren.

    Attributes
    ----------
    button : digitalio.DigitalInOut
        GPIO-Objekt, mit dem der Knopf abgefragt werden kann.
    carillon : Carillon
        Carillon, über das die Melodie gespielt wird.
    client : MqttClient
        MQTT-Client, über den der Knopfzustand mitgeteilt wird.
    played_time : float
        Letzter Zeitpunkt, zu dem die Melodie abgespielt wurde. Wird benötigt,
        um eine Totzeit für die Melodie zu ermitteln.
    pressed : bool
        Abstrahiert den Knopfzustand.
    settings : BellSettings
        Einstellungsobjekt, das individuelle Anpassungen enthält.

    Methods
    -------
    play()
        Spielt die Klingelmelodie ab.
    _loop()
        Interne Methode, die immer wieder den Status prüft.
    _publish_btn_state(state)
        Teilt dem MQTT-Server einen bestimmten Status mit.
    """

    def __init__(self, carillon: Carillon, client: MqttClient):
        """
        Erstellt das Objekt und einen Thread, der auf Knopfänderungen reagiert.

        Parameters
        ----------
        carillon : Carillon
            Carillon, auf dem Melodien ggf. abgespielt werden.
        client : MqttClient
            MQTT-Client, über den Informationen über den Knopfzustand
            publiziert werden.
        """

        # Alles folgende nur vorbereiten, wenn GPIO erwünscht ist
        self.settings: BellSettings = Settings().bell
        if self.settings.button is None: return

        # Nachträgliches Importieren der RPi-spezifischen Bibliotheken
        globals()['board'] = import_module('board')
        globals()['digitalio'] = import_module('digitalio')

        # Knopf-Eingang vorbereiten
        self.button = digitalio.DigitalInOut(
            board.__dict__[self.settings.button])
        self.button.direction = digitalio.Direction.INPUT

        # Vorbereiten des MQTT-Clients
        self.client: MqttClient = client
        self._publish_btn_state(False)

        self.carillon: Carillon = carillon
        self.played_time: float = 0
        Thread(target=self._loop, daemon=True).start()

    @property
    def pressed(self) -> bool:
        """
        Abstrahiert den Knopfzustand: hier nämlich invertiert (`False` bedeutet
        gedrückt).
        """
        return not self.button.value

    def play(self) -> None:
        """
        Spielt eine Melodie, sobald das gewollt ist - allerdings wird zuvor
        geprüft, ob die Totzeit durch ist.
        """
        if self.settings.melody is None: return

        if time.time() - self.played_time < self.settings.playtime: return
        self.played_time = time.time()

        melody = Melody.from_file(self.settings.melody)
        melody.transpose = self.settings.transpose
        melody.tempo = self.settings.tempo
        self.carillon.play(melody, self.settings.priority)

    def _loop(self) -> None:
        """Interne Methode, die dauerhaft läuft und den Knopfstatus prüft."""
        while True:
            time.sleep(0.1)

            if self.pressed:
                self._publish_btn_state(True)
                self.play()
                while self.pressed:
                    time.sleep(0.1)
                self._publish_btn_state(False)

    def _publish_btn_state(self, state: bool) -> None:
        """Interne Methode, die einen Knopf-Status published."""
        if self.client.client is None: return
        payload = '1' if state else '0'
        self.client.publish('bell/state', payload.encode('utf-8'))
