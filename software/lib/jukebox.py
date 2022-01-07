from glob import glob
from pathlib import Path
from typing import List

from .carillon import Carillon
from .melody import Melody
from .mqttclient import MqttClient
from .settings import Settings


class Jukebox:
    """
    Mittelsmann zwischen MQTT-Client und Carillon, das gezielt einzelne
    Melodien wiedergeben kann.

    Attributes
    ----------
    carillon : Carillon
        Carillon, auf dem gespielt wird.
    client : MqttClient
        MqttClient, der die Verbindung zum Server herstellt.
    settings : Settings
        Eintellungsobjekt, das globale Einstellungen beibehält.
    transpose : int
        Transponierung für die folgenden Melodien.

    Methods
    -------
    list() : List[str]
        Listet alle verfügbaren Lieder ab.
    play(song)
        Spielt ein bestimmtes Lied ab.
    _publish_transpose()
        Interne Methode, die die aktuelle Transponierung via MQTT broadcastet.
    _on_message(topic, payload)
        Interne Methode, die auf Nachrichten vom MQTT-Server reagiert.
    """

    def __init__(self, carillon: Carillon, client: MqttClient):
        """
        Erstellt die Jukebox und meldet sich beim MQTT-Client an.

        Parameters
        ----------
        carillon : Carillon
            Carillon-Objekt, auf dem gespielt wird.
        client : MqttClient
            MQTT-Client, über den die Nachrichten abgegriffen werden.
        """
        self.settings: Settings = Settings()
        self.carillon: Carillon = carillon
        self.client: MqttClient = client
        self.transpose: int = 0

        topics = ('play', 'stop', 'list/get', 'transpose/set', 'transpose/get')
        topics = [f'jukebox/{t}' for t in topics]
        self.client.subscribe(self._on_message, *topics)

    def list(self) -> List[str]:
        """
        Listet alle verfügbaren Melodien auf, die der Jukebox zur Verfügung
        stehen.

        Returns
        -------
        Liste aller Melodien, die zur Verfügung stehen.
        """
        songs = glob(f'{self.settings.jukebox_basefolder}/*.mid')
        return [Path(s).stem for s in songs]

    def play(self, song: str) -> None:
        """
        Spielt eine Melodie ab, die über den Namen gefunden wird.

        Parameters
        ----------
        song : str
            Name des Liedes, das abgespielt werden soll.
        """
        path = Path(f'{self.settings.jukebox_basefolder}/{song}.mid')
        if not path.exists(): return
        melody = Melody.from_file(path)
        melody.transpose = self.transpose
        self.carillon.play(melody, self.settings.jukebox_priority)

    def _publish_transpose(self) -> None:
        """Interne Methode, die die aktuelle Transponierung broadcasten."""
        payload = str(self.transpose).encode('utf-8')
        self.client.publish('jukebox/transpose', payload)

    def _on_message(self, topic: str, payload: bytes) -> None:
        """Internes Callback, das auf Nachrichten des MQTT-Servers reagiert."""
        topic = topic.removeprefix(f'jukebox/')
        if topic == 'play':
            self.play(payload.decode('utf-8'))
        elif topic == 'stop':
            self.carillon.stop()
        elif topic == 'list/get':
            payload = '\n'.join(self.list()).encode('utf-8')
            self.client.publish('jukebox/list', payload)
        elif topic == 'transpose/set':
            self.transpose = int(payload.decode('utf-8'))
            self._publish_transpose()
        elif topic == 'transpose/get':
            self._publish_transpose()
