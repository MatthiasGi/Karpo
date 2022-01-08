from datetime import datetime, timedelta
from pathlib import Path
import schedule
from threading import Thread
import time

from .carillon import Carillon
from .melody import Melody
from .settings import Settings


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
    settings : Settings
        Einstellungsobjekt, das globale Einstellungen bereithält.
    theme : str
        Theme, das die Geläutart vorgibt.

    Methods
    -------
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
        self.settings: Settings = Settings()

        for q in range(0, 60, 15):
            schedule.every().hour.at(f':{q:02d}').do(self._strike)

        def thread():
            while True:
                schedule.run_pending()
                time.sleep(0.1)

        Thread(target=thread, daemon=True).start()

    @property
    def basefolder(self) -> Path:
        """Ordner, in dem sich die Theme-Ordner befinden."""
        return Path(self.settings.striker_basefolder)

    @property
    def folder(self) -> Path:
        """Ordner, in dem sich die aktuellen Theme-Dateien befinden."""
        return self.basefolder / self.settings.striker_theme

    @property
    def theme(self) -> str:
        """Name des aktuell verwendeten Themes."""
        return self.settings.striker_theme

    @theme.setter
    def theme(self, value: str) -> None:
        """Stellt ein neue Theme ein, sofern das vorhanden ist."""
        path = self.basefolder / value
        if path.is_dir(): self.settings.striker_theme = value

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
            hours %= 12
            if hours == 0: hours = 12
            if hpath.exists(): melody += Melody.from_file(hpath) * hours

        # Melodie wiedergeben
        self.carillon.play(melody, self.settings.striker_priority)
