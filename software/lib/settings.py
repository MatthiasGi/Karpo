import json
from pathlib import Path
from pydantic import BaseModel, BaseSettings, Extra, root_validator
from pydantic.env_settings import SettingsSourceCallable
from typing import Any, Dict, Tuple


class AngelusSettings(BaseModel):
    """
    Einstellungen für den Angelus.

    Attributes
    ----------
    times : str
        Kommagetrennte Liste von Zeiten, an deren Schlagwerkzeit sich ein
        Angelus anschließen soll. Bei None gibt's keinen Angelus.
    path : str
        Pfad zum Angeluslied.
    transpose : int
        Transponierung des Angelus.
    tempo : float
        Tempoanpassung des Angelus.
    """
    times: str = None
    path: str = '../melodies/songs/Lourdes Lied.mid'
    transpose: int = 0
    tempo: float = 1


class BellSettings(BaseModel):
    """
    Einstellungen für die GPIO-Klingelfunktion.

    Attributes
    ----------
    button : str
        Pinbezeichnung, an der der Klingeleingang liegt (bspw. `'D26'`). Falls
        `None`, wird das Modul gar nicht geladen.
    melody : str
        Pfad zur abzuspielenden Melodie beim Drücken der Klingel. Wenn nur über
        MQTT informiert werden soll, dann hier auf `None` setzen.
    playtime : float
        Anzahl an Sekunden, die der Button keinen neuen Klingelton auslösen
        soll.
    transpose : int
        Transponierungseinstellung für die abzuspielende Melodie.
    tempo : float
        Tempoeinstellung für die abzuspielende Melodie.
    priority : int
        Priorität der abzuspielenden Melodie.
    """
    button: str = None
    melody: str = '../melodies/songs/Westminster Quarters.mid'
    playtime: float = 10
    transpose: int = 0
    tempo: float = 1
    priority: int = 10


class DirektoriumSettings(BaseModel):
    """
    Einstellungen für das Direktorium.

    Attributes
    ----------
    cachedir : str
        Verzeichnis, in dem die Feste gecachet werden können.
    eastermute : bool
        Ob eine Osterstille zu Karfreitag und Karsamstag eingehalten werden
        soll.
    kalender : str
        Kalenderbezeichnung für die Kalender-API.
    theme_nichtgeboten : str
        Schlagwerktheme, das an nichtgebotenen Gedenktagen genutzt werden soll.
    theme_geboten : str
        Schlagwerktheme, das an gebotenen Gedenktagen genutzt werden soll.
    theme_fest : str
        Schlagwerktheme, das an Festen genutzt werden soll.
    theme_hochfest : str
        Schlagwerktheme, das an Hochfesten genutzt werden soll.
    theme_sonntag : str
        Schlagwerktheme für einen nicht anders belegten Sonntag.
    antiphon : str
        Zeit, nach deren Angabe die aktuelle marianische Antiphon gespielt
        werden soll. Bei None wird sie gar nicht gespielt.
    antiphon_christmas : str
        Pfad zur Antiphon für die Weihnachtszeit (Alma redemptoris mater).
    antiphon_lent : str
        Pfad zur Antiphon für die Fastenzeit (Ave Regina caelorum).
    antiphon_easter : str
        Pfad zur Antiphon für die Osterzeit (Regina caeli laetare).
    antiphon_ordinary : str
        Pfad zur Antiphon für die nichtgeprägten Zeiten (Salve Regina).
    antiphon_transpose : int
        Globale Transponierung der Antiphonen.
    antiphon_tempo : float
        Globale Tempoanpassung der Antiphonen.
    """
    cachedir: str = './cache'
    eastermute: bool = False
    kalender: str = 'deutschland'
    theme_nichtgeboten: str = None
    theme_geboten: str = None
    theme_fest: str = None
    theme_hochfest: str = None
    theme_sonntag: str = None
    antiphon: str = '21:00'
    antiphon_christmas: str = '../melodies/songs/Alma Redemptoris Mater.mid'
    antiphon_lent: str = '../melodies/songs/Ave Regina caelorum.mid'
    antiphon_easter: str = '../melodies/songs/Regina caeli laetare.mid'
    antiphon_ordinary: str = '../melodies/songs/Salve Regina.mid'
    antiphon_transpose = 0
    antiphon_tempo = 1


class FestiveSettings(BaseModel, extra=Extra.allow):
    """
    Einstellungen für den Fest-Player.

    Attributes
    ----------
    festives : Dict[str, Dict[str, Any]]
        Melodien, die zu Festen eingebaut werden sollen.
    """
    festives: Dict[str, Dict[str, Any]] = dict()


class JukeboxSettings(BaseModel):
    """
    Einstellungen für die Jukebox.

    Attributes
    ----------
    priority : int
        Mit welcher Priorität die Melodien aus der Jukebox abgespielt werden
        sollen.
    basefolder : str
        Pfad, in dem die Jukebox nach Melodien sucht.
    """
    priority: int = 5
    basefolder: str = '../melodies/songs'


class MqttSettings(BaseModel):
    """
    Einstellungen für den MQTT-Client.

    Attributes
    ----------
    id : str
        Eindeutige Bezeichnung für den MQTT-Client.
    server : str
        Adresse des MQTT-Brokers. Falls diese `None` ist, wird das MQTT-Modul
        abgeschaltet.
    port : int
        Port des MQTT-Brokers.
    basetopic : str
        Basispfad, an den alle Pfade angehängt werden zur besseren
        Unterscheidung.
    user : str
        Optionaler Benutzer für die Authentifizierung beim MQTT-Broker.
    password : str
        Optionales Passwort für die Authentifizierung beim MQTT-Broker.
    controller : bool
        Ob der Controller für einfache Einstellungsänderungen geladen werden
        soll.
    control_volume : float
        Einstellung der Lautstärke des Carillons, so, wie sie durch den
        Controller angepasst wurde
    """
    id: str = 'Karpo'
    server: str = None
    port: int = 1883
    basetopic: str = 'karpo'
    user: str = None
    password: str = None
    controller: bool = True
    control_volume: float = 1


class StrikerSettings(BaseModel, extra=Extra.allow):
    """
    Einstellungen für das Schlagwerk.

    Attributes
    ----------
    priority : int
        Mit welcher Priorität der Stundenschlag abgespielt werden soll.
    basefolder : str
        Pfad, in dem die verschiedenen Stile von Stundenschlägen liegen.
    theme : str
        Aktuell ausgewählter Stil für Stundenschläge.
    themes : Dict[str, Dict[str, Any]]
        Einstellungen für konkrete Themes - Dokumentation dazu siehe in der
        Striker-Klasse.
    nightmuter_start : str
        Startzeit, um die die Nachtabschaltung erfolgen soll.
    nightmuter_end : str
        Zeit, um die die Nachtabschaltung aufgehoben werden soll.
    """
    priority: int = -1
    basefolder: str = '../melodies/striker'
    theme: str = 'default'
    themes: Dict[str, Dict[str, Any]] = dict()
    nightmuter_start: str = '21:00'
    nightmuter_end: str = '8:00'


class Settings(BaseSettings):
    """
    Klasse, die die Projekteinstellungen enthält. Diese werden hier mit
    Standardwerten vorbelegt und dokumentiert.

    Attributes
    ----------
    angelus : AngelusSettings
        Einstellungen für den Angelus.
    bell : BellSettings
        Einstellungen für eine Hardware-Klingel via GPIO-Pins.
    direktorium : DirektoriumSettings
        Einstellungen für das Direktorium.
    festive : FestiveSettings
        Einstellungen für den Festplayer.
    jukebox : JukeboxSettings
        Einstellungen für die Jukebox.
    mqtt : MqttSettings
        Einstellungen für den MQTT-Client.
    striker : StrikerSettings
        Einstellungen für das Schlagwerk.

    Class Methods
    -------------
    save_settings(values) : Dict[str, Any]
        Speichert veränderte Einstellungen in der Konfigurationsdatei.

    Inner Classes
    -------------
    Config
        Interne Einstellungen für die Einstellungsklasse.
    """

    angelus: AngelusSettings = AngelusSettings()
    bell: BellSettings = BellSettings()
    direktorium: DirektoriumSettings = DirektoriumSettings()
    festive: FestiveSettings = FestiveSettings()
    jukebox: JukeboxSettings = JukeboxSettings()
    mqtt: MqttSettings = MqttSettings()
    striker: StrikerSettings = StrikerSettings()

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
        if not path.exists(): return values

        encoding = cls.__config__.cfg_file_encoding
        ascii = cls.__config__.cfg_file_ascii

        def serialize_basemodel(model: BaseModel):
            if isinstance(model, BaseModel):
                return model.dict()
            else:
                raise TypeError(f'{type(model)} is not serializable!')

        with path.open('w', encoding=encoding) as f:
            json.dump(values, f, ensure_ascii=ascii, indent=2,
                      default=serialize_basemodel)
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
        env_nested_delimiter = '__'
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
