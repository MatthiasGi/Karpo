import json
from pathlib import Path
from pydantic import BaseSettings, root_validator
from pydantic.env_settings import SettingsSourceCallable
from typing import Any, Dict, Tuple


class Settings(BaseSettings):
    """
    Klasse, die die Projekteinstellungen enthält. Diese werden hier mit
    Standardwerten vorbelegt und dokumentiert.

    Attributes
    ----------
    mqtt_id : str
        Eindeutige Bezeichnung für den MQTT-Client.
    mqtt_server : str
        Adresse des MQTT-Brokers. Falls diese `None` ist, wird das MQTT-Modul
        abgeschaltet.
    mqtt_port : int
        Port des MQTT-Brokers.
    mqtt_basetopic : str
        Basispfad, an den alle Pfade angehängt werden zur besseren
        Unterscheidung.
    mqtt_user : str
        Optionaler Benutzer für die Authentifizierung beim MQTT-Broker.
    mqtt_password : str
        Optionales Passwort für die Authentifizierung beim MQTT-Broker.
    jukebox_priority : int
        Mit welcher Priorität die Melodien aus der Jukebox abgespielt werden
        sollen.
    jukebox_basefolder : str
        Pfad, in dem die Jukebox nach Melodien sucht.
    striker_priority : int
        Mit welcher Priorität der Stundenschlag abgespielt werden soll.
    striker_basefolder : str
        Pfad, in dem die verschiedenen Stile von Stundenschlägen liegen.
    striker_theme : str
        Aktuell ausgewählter Stil für Stundenschläge.

    Class Methods
    -------------
    save_settings(values) : Dict[str, Any]
        Speichert veränderte Einstellungen in der Konfigurationsdatei.

    Inner Classes
    -------------
    Config
        Interne Einstellungen für die Einstellungsklasse.
    """
    mqtt_id: str = 'Karpo'
    mqtt_server: str = None
    mqtt_port: int = 1883
    mqtt_basetopic: str = 'karpo'
    mqtt_user: str = None
    mqtt_password: str = None

    jukebox_priority: int = 5
    jukebox_basefolder: str = '../melodies/songs'

    striker_priority: int = -1
    striker_basefolder: str = '../melodies/striker'
    striker_theme: str = 'westminster'

    @root_validator
    def save_settings(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Nutzt einen Trick zur Speicherung veränderter Einstellungen: die
        Methode gibt vor, ein Validator zu sein, der veränderte Einstellungen
        überprüfen muss. Diese werden jedoch immer als gültig zurückgegeben, en
        passant lassen sich alle Einstellungen aber abspeichern. Sollte keine
        Konfigurationsdatei existieren, wird auch keine angelegt. Vermutlich
        nutzt der Anwender eine andere Methode zum Einspeisen der
        Einstellungen.

        Parameters
        ----------
        values : Dict[str, Any]
            Die veränderten Einstellungen, die abgespeichert werden sollen.

        Returns
        -------
        Die gleichen Einstellungen ohne irgendwelche Veränderungen.
        """
        path = cls.__config__.cfg_file_path
        if path.exists():
            encoding = cls.__config__.cfg_file_encoding
            ascii = cls.__config__.cfg_file_ascii
            with path.open('w', encoding=encoding) as f:
                json.dump(values, f, ensure_ascii=ascii, indent=2)
        return values

    class Config:
        """
        Interne Klasse, die Einstellungen für die Anwendung der
        Einstellungsregistry bereit hält.

        Attributes
        ----------
        cfg_file_ascii : bool
            Ob beim Abspeichern darauf geachtet werden soll, dass nur
            ASCII-Zeichen in den Einstellungen enthalten sind. Auf False
            setzen, falls als Encoding UTF-8 genutzt wird.
        cfg_file_encoding : str
            Encoding für die Konfigurationsdatei. UTF-8 bietet sich dafür
            natürlich besonders an…
        cfg_file_path : Path
            Pfadobjekt zur Konfigurationsdatei.
        env_prefix : str
            Von pydantic vorgegebenes Attribut zur Angabe eines Präfixes von
            Umgebungsvariablen.
        validate_assignment : bool
            Durch pydantic vorgegeben und unbedingt auf `True` zu setzen, damit
            der Validator oben zum Speichern der Einstellungen immer aufgerufen
            wird.

        Class Methods
        -------------
        customise_sources(init_settings, env_settings, file_secret_settings)
                : Tuple[SettingsSourceCallable, ...]
            Organisiert die Quellen für Einstellungsparameter neu.
        json_config_settings_source(settings) : Dict[str, Any]
            Liest die Einstellungen aus einer JSON-Konfigurationsdatei.
        """

        cfg_file_ascii: bool = False
        cfg_file_encoding: str = 'utf-8'
        cfg_file_path: Path = Path('config.json')
        env_prefix: str = 'karpo_'
        validate_assignment: bool = True

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable
        ) -> Tuple[SettingsSourceCallable, ...]:
            """Ordnet die Reihenfolge der Einstellungseingänge neu."""
            return init_settings, env_settings, cls.json_config_settings_source

        @classmethod
        def json_config_settings_source(cls, settings) -> Dict[str, Any]:
            """
            Liest die Einstellungen aus einer JSON-Datei mit dem oben
            definierten Pfad `cfg_file_path` und lädt diese in das
            Einstellungsobjekt unten ein. Sofern keine Konfigurationsdatei
            existiert, wird diese Arbeit übersprungen, es wird also nur auf die
            Standardeinstellungen zugegriffen.

            Parameters
            ----------
            settings : BaseSettings
                Das Objekt, auf dessen Einstellungen die Konfigurationsdatei-
                Einstellungen angewendet werden sollen.

            Returns
            -------
            Die eingelesenen Einstellungen.
            """
            path = cls.cfg_file_path
            if not path.exists(): return dict()
            return json.loads(path.read_text(cls.cfg_file_encoding))
