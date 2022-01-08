from .mqttclient import MqttClient
from .settings import MqttSettings, Settings
from .striker import Striker


class MqttController:
    """
    Klasse, die MQTT und Striker zusammenbringt, indem sie über MQTT einige
    Optionen zum Bearbeiten anbietet.

    Attributes
    ----------
    client : MqttClient
        MQTT-Client, über den Nachrichten ausgetauscht werden.
    settings : MqttSettings
        Einstellungsobjekt mit Anpassungen.
    striker : Striker
        Schlagwerk, an dem Einstellungen verändert werden.

    Methods
    -------
    _on_message(topic, payload)
        Interner Callback, der auf ankommende Nachrichten reagiert.
    _publish_theme()
        Teilt dem MQTT-Server das verwendete Theme mit.
    _publish_volume()
        Teilt dem MQTT-Server die eingestellte Lautstärke mit.
    """

    def __init__(self, striker: Striker, client: MqttClient):
        """
        Bereitet das Objekt vor und registriert sich zur Vermittlung beim
        MQTT-Client.

        Parameters
        ----------
        striker : Striker
            Schlagwerk, das angepasst können werden soll.
        client : MqttClient
            MQTT-Client, über den Anfragen ankommen.
        """
        self.striker: Striker = striker
        self.client: MqttClient = client
        self.settings: MqttSettings = Settings().mqtt

        topics = ('volume/get', 'volume/set', 'stop', 'theme/get',
                  'theme/list/get', 'theme/set')
        topics = [f'control/{t}' for t in topics]
        self.client.subscribe(self._on_message, *topics)

        self.striker.carillon.volume = self.settings.control_volume

    def _on_message(self, topic: str, payload: bytes) -> None:
        """Interner Callback, der auf ankommende Nachrichten reagiert."""
        topic = topic.removeprefix(f'control/')
        if topic == 'volume/get':
            self._publish_volume()
        elif topic == 'volume/set':
            self.striker.carillon.volume = float(payload.decode('utf-8'))
            self._publish_volume()
        elif topic == 'stop':
            self.striker.carillon.stop()
        elif topic == 'theme/get':
            self._publish_theme()
        elif topic == 'theme/list/get':
            dirs = list(self.striker.basefolder.glob('**'))[1:]
            payload = '\n'.join([d.name for d in dirs]).encode('utf-8')
            self.client.publish('theme/list', payload)
        elif topic == 'theme/set':
            self.striker.theme = payload.decode('utf-8')
            self._publish_theme()

    def _publish_theme(self) -> None:
        """Teilt dem MQTT-Server das verwendete Theme mit."""
        theme = self.striker.theme
        self.client.publish('control/theme', theme.encode('utf-8'))

    def _publish_volume(self) -> None:
        """Teilt dem MQTT-Server die eingestellte Lautstärke mit."""
        vol = self.striker.carillon.volume
        self.client.publish('control/volume', str(vol).encode('utf-8'))
