from datetime import datetime, timedelta
from pathlib import Path
import schedule
from threading import Thread
import time
from typing import Callable, List

from .carillon import Carillon
from .melody import Melody
from .settings import Settings, StrikerSettings


class Striker:
    """
    Virtuelles Schlagwerk, das jede Viertelstunde auslöst. Anhand eines Themes
    kann ein Geläutstil ausgewählt werden.

    Attributes
    ----------
    basefolder : Path
        Pfad, in dem die einzelnen Themes bereitstehen.
    carillon : Carillon
        Das Carillon, auf dem geschlagen werden soll.
    folder : Path
        Pfad des Ordners mit aktuellem Theme.
    observers : List[Callable[[Melody, int, int], Melody]]
        Liste an registrierten Observern für einen Schlag.
    settings : StrikerSettings
        Einstellungsobjekt, das globale Einstellungen bereithält.
    theme : str
        Theme, das die Geläutart vorgibt.

    Methods
    -------
    subscribe(observer)
        Registriert eine Callbackmethode.
    _strike()
        Interne Methode zum Auslösen des eigentlichen Stundengeläuts.
    """

    def __init__(self, carillon: Carillon):
        """
        Erstellt das Stundengeläut und bereitet den Scheduler vor. Es wird ein
        Thread gestartet, der automatisch den Scheduler anstößt.

        Parameters
        ----------
        carillon : Carillon
            Carillon-Objekt, auf dem gespielt wird.
        """
        self.carillon: Carillon = carillon
        self.settings: StrikerSettings = Settings().striker
        self.observers: List[Callable[[Melody, int, int], Melody]] = list()

        for q in range(0, 60, 15):
            schedule.every().hour.at(f':{q:02d}').do(self._strike)

        def thread() -> None:
            while True:
                schedule.run_pending()
                time.sleep(0.1)

        Thread(target=thread, daemon=True).start()

    @property
    def basefolder(self) -> Path:
        """Ordner, in dem sich die Theme-Ordner befinden."""
        return Path(self.settings.basefolder)

    @property
    def folder(self) -> Path:
        """Ordner, in dem sich die aktuellen Theme-Dateien befinden."""
        return self.basefolder / self.theme

    @property
    def theme(self) -> str:
        """Name des aktuell verwendeten Themes."""
        return self.settings.theme

    @theme.setter
    def theme(self, value: str) -> None:
        """Stellt ein neue Theme ein, sofern das vorhanden ist."""
        path = self.basefolder / value
        if path.is_dir(): self.settings.theme = value

    def subscribe(
        self, observer: Callable[[Melody, int, int], Melody]
    ) -> None:
        """
        Registriert eine Methode, die über auszuführende Schläge informiert
        werden soll. Sie muss die Parameter Melodie, Stundenzahl und
        Viertelstundenzahl aufnehmen.

        Parameters
        ----------
        observer : Callable[[Melody, int, int], Melody]
            Callback-Methode, die informiert werden soll.
        """
        self.observers.append(observer)

    def _strike(self) -> None:
        """Interne Methode, die das eigentliche Stundengeläut auslöst."""

        # Ermitteln der Anzahl an Stunden- und Viertelstundenschlägen
        time = datetime.now() + timedelta(minutes=7, seconds=30)
        hours, quarters = time.hour, time.minute // 15
        print(f'Striking: {hours:02d}:{quarters * 15:02d}')

        # Viertelstundenschläge in Melodie einladen
        melody = Melody()
        qpath = self.folder / f'q{quarters if quarters != 0 else 4}.mid'
        if qpath.exists(): melody += Melody.from_file(qpath)

        # Bei Bedarf Stundenschlag anfügen
        if quarters == 0:
            hpath = self.folder / 'h.mid'
            h = hours % 12
            if h == 0: h = 12
            if hpath.exists(): melody += Melody.from_file(hpath) * h

        # Ggf. Einstellungen für die Melodie übernehmen
        if self.theme in self.settings.themes:
            cfg = self.settings.themes[self.theme]
            if 'transpose' in cfg: melody.transpose = cfg['transpose']
            if 'tempo' in cfg: melody.tempo = cfg['tempo']

        # Alle Observer noch um ihre Meinung fragen und ggf. abbrechen
        for o in self.observers: melody = o(melody, hours, quarters)
        if melody is None: return

        # Melodie wiedergeben
        self.carillon.play(melody, self.settings.priority)
