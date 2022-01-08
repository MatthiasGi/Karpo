from dataclasses import dataclass
from datetime import date, timedelta
import json
import os
import requests
from typing import List

from .event import Event
from .season import Season


@dataclass
class Direktorium:
    """
    Stellt das Direktorium mit einem Cache und einem Regionalkalender zur
    Verfügung.

    Attributes
    ----------
    kalender : str
        Kalenderbezeichnung nach
        https://www.eucharistiefeier.de/lk/api-abfrage.php.
    cache_dir : str
        Verzeichnis, in dem Ergebnisse zwischengespeichert werden sollen.

    Methods
    -------
    get(d) : List[Event]
        Gibt eine Liste von Events für ein Datum zurück.
    request_api(year, month, day) : requests.models.Response
        Fragt die API online über ein Datum ab.
    request_cache(d) : dict
        Erstellt das API-Format aus dem Cache.
    season(d) : Season
        Ermittelt die Zeit im Kirchenjahr, in die das Datum fällt.

    Static Methods
    --------------
    easter(year) : date
        Ermittelt das Osterdatum für ein gegebenes Jahr.
    """

    kalender: str = 'deutschland'
    cache_dir: str = None

    def get(self, d: date) -> List[Event]:
        """Gibt eine Liste von Events für ein angegebenes Datum zurück."""
        r = self.request_cache(d)
        entries = [Event.parse(e) for e in r.json()['Zelebrationen'].values()]
        entries.sort(key=lambda e: e.importance)
        return entries

    def request_api(
        self, year: int, month: int = None, day: int = None
    ) -> requests.models.Response:
        """
        Fragt die API online direkt ab, optional können Monat und Tag angegeben
        werden.
        """
        url = 'http://www.eucharistiefeier.de/lk/api.php?format=json&' \
              f'info=wdtrgflu&dup=e&bahn=j&kal={self.kalender}&jahr={year}&'
        if month: url += f'monat={month}&'
        if month and day: url += f'tag={day}&'
        return requests.get(url)

    def request_cache(self, d: date) -> dict:
        """
        Erstellt das API-Format aus dem Cache. Falls benötigt wird dazu der
        Cache angelegt. Sollte kein Cache vorgesehen sein, wird direkt die
        Online-API abgefragt.
        """
        if self.cache_dir is None:
            return self.request_api(d.year, d.month, d.day)

        # Daten einlesen (ggf. herunterladen)
        dir = os.path.join(self.cache_dir, self.kalender)
        file = os.path.join(dir, f'{d.year}.json')
        if not os.path.exists(file):
            if not os.path.exists(dir): os.makedirs(dir)
            r = self.request_api(d.year)
            with open(file, 'wb') as f: f.write(r.content)
            data = r.json()
        else:
            with open(file) as f: data = json.load(f)

        # Dictionary für aktuellen Tag konstruieren
        datestr = d.isoformat()
        data['Zelebrationen'] = {k: v for k, v in data['Zelebrationen'].items()
                                 if datestr == v['Datum']}
        return data

    def season(self, d: date) -> Season:
        """
        Ermittelt die Zeit im Kirchenjahr, in die das gegebene Datum fällt.
        """
        christmas = date(d.year, 12, 25)
        advent = christmas - timedelta(days=21 + christmas.isoweekday())
        if d >= advent: return Season.CHRISTMAS

        epiphany = date(d.year, 1, 6)
        baptism = epiphany + timedelta(days=7 - epiphany.isoweekday() % 7)
        if d <= baptism: return Season.CHRISTMAS

        easter = Direktorium.easter(d.year)
        ashwednsday = easter - timedelta(days=46)
        if d >= ashwednsday and d < easter: return Season.LENT

        pentecoste = easter + timedelta(days=49)
        if d >= easter and d <= pentecoste: return Season.EASTER

        return Season.ORDINARY

    @staticmethod
    def easter(year: int) -> date:
        """Ermittelt das Osterdatum für ein Jahr."""
        a, b, c = year % 19, year // 100, year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        return date(year, f // 31, f % 31 + 1)
