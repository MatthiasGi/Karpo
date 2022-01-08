from datetime import date, timedelta
from typing import List

from .direktorium import Direktorium
from .event import Event
from .season import Season


class TodayDirektorium(Direktorium):
    """
    Eine Erweiterung der Direktoriumsklasse, die Ausgaben auf den heutigen Tag
    bezieht und cacht.

    Attributes
    ----------
    _last_date : date
        Letztes Datum, zu dem gecacht wurde.
    _last_get : List[Event]
        Eventliste des gecachten Tages.
    _last_season : Season
        Zeit im Kirchenjahr des gecachten Tages.
    _last_easter : date
        Osterdatum des aktuellen Jahres.

    Methods
    -------
    easter() : date
        Cacht das aktuelle Osterdatum.
    get() : List[Event]
        Gibt die Events des heutigen Tages zurück.
    season() : Season
        Gibt die Zeit im Kirchenjahr des heutigen Tages zurück.
    _check()
        Interne Methode, die das cachen nachhält.
    """

    def __init__(self, *params, **kwargs):
        """Erstellt das Objekt und bereitet das Caching vor."""
        super().__init__(*params, **kwargs)
        self._last_date = date.today() - timedelta(days=1)

    def easter(self) -> date:
        """Cacht das Osterdatum für das aktuelle Jahr."""
        self._check()
        return self._last_easter

    def get(self) -> List[Event]:
        """Gibt eine Liste von heute stattfindenden Events zurück."""
        self._check()
        return self._last_get

    def season(self) -> Season:
        """Ermittelt die aktuelle Zeit im Kirchenjahr."""
        self._check()
        return self._last_season

    def _check(self) -> None:
        """
        Interne Methode, die überprüft, ob gecacht werden muss und dies ggf.
        tut.
        """
        today = date.today()
        if self._last_date >= today: return
        self._last_get = super().get(today)
        self._last_season = super().season(today)
        self._last_easter = Direktorium.easter(today.year)
        self._last_date = today
