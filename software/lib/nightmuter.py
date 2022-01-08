from .melody import Melody
from .settings import Settings, StrikerSettings
from .striker import Striker


class Nightmuter:
    """
    Einfache Klasse zur Realisierung einer Nachtabschaltung.

    Attributes
    ----------
    end_hour : int
        Stundenzahl, um die die Nachtabschaltung enden soll.
    end_quarter : int
        Quartalsnummer, um die die Nachtabschaltung enden soll.
    settings : StrikerSettings
        Einstellungsobjekt, das Informationen über Start- und Endzeit enthält.
    start_hour : int
        Stundenzahl, um die die Nachtabschaltung beginnen soll.
    start_quarter : int
        Quartalsnummer, um die die Nachtabschaltung beginnen soll.

    Methods
    -------
    _check_mute(melody, hours, quarters) : Melody
        Interne Methode, die vom Schlagwerk zur Überprüfung aufgerufen wird.
    """

    def __init__(self, striker: Striker):
        """
        Registriert sich beim Schlagwerk als Callback zur Überprüfung der
        Nachtabschaltung.
        """
        self.settings: StrikerSettings = Settings().striker
        striker.subscribe(self._check_mute)

    @property
    def end_hour(self) -> int:
        """Stunde, um die die Nachtabschaltung enden soll."""
        return int(self.settings.nightmuter_end.split(':')[0])

    @property
    def end_quarter(self) -> int:
        """Quartal, zu dem die Nachtabschaltung enden soll."""
        minute = int(self.settings.nightmuter_end.split(':')[1])
        return minute // 15

    @property
    def start_hour(self) -> int:
        """Stunde, um die die Nachtabschaltung starten soll."""
        return int(self.settings.nightmuter_start.split(':')[0])

    @property
    def start_quarter(self) -> int:
        """Quartal, zu dem die Nachtabschaltung starten soll."""
        minute = int(self.settings.nightmuter_start.split(':')[1])
        return minute // 15

    def _check_mute(self, melody: Melody, hours: int, quarters: int) -> Melody:
        """
        Callbackmethode, die überprüft, ob ein Schlag in die Nachtzeit fällt
        und ihn ggf. abbricht.
        """
        if self.start_hour < hours: return None
        if self.start_hour == hours and self.start_quarter < quarters:
            return None
        if self.end_hour > hours: return None
        if self.end_hour == hours and self.end_quarter > quarters: return None
        return melody
