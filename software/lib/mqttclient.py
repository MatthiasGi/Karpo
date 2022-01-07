import paho.mqtt.client as mqtt
from typing import Any, Callable, Dict

from .settings import Settings


class MqttClient:
    """
    Klasse, die die Kommunikation mit dem MQTT-Broker abstrahiert. Sie
    bietet das Listener-Paradigma an, um andere Klassen über eingehende
    Nachrichten gezielt zu informieren.

    Attributes
    ----------
    connected : bool
        Gibt an, ob eine Verbindung erfolgreich aufgebaut wurde.
    client : mqtt.Client
        Das MQTT-Client-Objekt, mit dem eigentlich interagiert wird.
    settings : Settings
        Einstellungsobjekt, über das die MQTT-Einstellungen abgefragt werden.
    _subscriptions : Dict[str, Callable[[str, bytes], None]]
        Objekt, das alle von Callbacks abgehorchten Kanäle enthält.

    Methods
    -------
    publish(topic, payload, qos, retain)
        Broadcastet eine MQTT-Nachricht.
    subscribe(callback, *topics)
        Lässt in Zukunft ein Callback über eingehende Nachrichten zu Topics
        informieren.
    _on_connect(client, userdata, flags, rc)
        Internes Callback bei Verbindungsaufbau.
    _on_message(client, userdata, msg)
        Internes Callback bei Nachrichteneingang.
    """

    def __init__(self):
        """
        Erstellt das Objekt und baut eine Verbindung zum MQTT-Server auf,
        sofern eine Server-Adresse über das Einstellungsobjekt zu erhalten ist.
        Ein Loop für die Abarbeitung der eintreffenden und ausgehenden
        Nachrichten wird asynchron gestartet.
        """
        self.settings: Settings = Settings()
        self.connected: bool = False
        self.client: mqtt.Client = None
        self._subscriptions: Dict[str, Callable[[str, bytes], None]] = dict()

        if not self.settings.mqtt_server: return
        self.client = mqtt.Client('Karpo', clean_session=False)
        if self.settings.mqtt_user:
            self.client.username_pw_set(
                self.settings.mqtt_user, self.settings.mqtt_password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.connect(
            self.settings.mqtt_server, self.settings.mqtt_port, keepalive=5)

        self.client.loop_start()

    def publish(
        self, topic: str, payload: bytes, qos: int = 0, retain: bool = False
    ) -> None:
        """
        Verbreitet eine Nachricht über das MQTT-Protokoll und stellt dem Topic
        automatisch das globale Basistopic voran.

        Parameters
        ----------
        topic : str
            Topic, zu dem publiziert wird.
        payload : bytes
            Zu übermittelnde Nachricht.
        qos : int (optional)
            Quality of Service-Level, standardmäßig 0.
        retain : bool (optional)
            Ob es sich um die „last known good“ bzw. retained-Nachricht
            handelt, standardmäßig nicht der Fall.
        """
        self.client.publish(f'{self.settings.mqtt_basetopic}/{topic}', payload,
                            qos=qos, retain=retain)

    def subscribe(
        self, callback: Callable[[str, bytes], None], *topics: str
    ) -> None:
        """
        Erlaubt einem Callback, auf ein bestimmtes Topic zu horchen.

        Parameters
        ----------
        callback : Callable[[str, bytes], None]
            Callback, das ausgeführt werden soll. Erster Parameter der Methode
            ist immer das Topic (bereinigt um globale Voranstellung), zweiter
            Parameter die eigentliche, unbearbeitete Payload.
        *topics : str
            Liste der Topics, über die das Callback informiert werden soll.
        """
        for t in topics:
            topic = f'{self.settings.mqtt_basetopic}/{t}'
            self._subscriptions[topic] = callback
            self.client.subscribe(topic)

    def _on_connect(
        self, client: mqtt.Client, userdata: Any, flags: dict, rc: int
    ) -> None:
        """Internes Callback, das bei Verbindungsaufbau ausgeführt wird."""
        if rc == 0: self.connected = True

    def _on_message(
        self, client: mqtt.Client, userdata: Any, msg: mqtt.client.MQTTMessage
    ) -> None:
        """Internes Callback, das Nachrichten entgegennimmt."""
        if msg.topic not in self._subscriptions: return
        topic = msg.topic.removeprefix(f'{self.settings.mqtt_basetopic}/')
        self._subscriptions[msg.topic](topic, msg.payload)
