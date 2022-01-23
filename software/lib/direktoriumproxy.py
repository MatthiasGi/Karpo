from datetime import date, timedelta
import schedule

from .direktorium.rank import Rank
from .direktorium.season import Season
from .direktorium.todaydirektorium import TodayDirektorium

from .melody import Melody
from .striker import Striker
from .settings import DirektoriumSettings, Settings


class DirektoriumProxy:
    """
    Verbindet das Direktorium mit dem Schlagwerk, indem es liturgische
    Fähigkeiten je nach Einstellungslage hinzufügen kann.

    Attributes
    ----------
    direktorium : TodayDirektorium
        Ein gecachtes Direktorium, das über den liturgischen Kalender Auskunft
        gibt.
    settings : DirektoriumSettings
        Einstellungsobjekt, in dem Anpassungen vorliegen.
    striker : Striker
        Schlagwerk, das angepasst werden soll.
    theme_modified : bool
        Ob das Theme vom Schlagwerk angepasst wurde - das erlaubt eine
        nachträgliche Rückanpassung.

    Methods
    -------
    _marianic_antiphon(melody, hours, quarters) : Melody
        Fügt bei Bedarf die passende marianische Antiphon an die Melodie an.
    _mute_easter(melody, hours, quarters) : Melody
        Stellt sicher, dass das Stundengeläut zum Triduum Paschale ruhig ist.
    _theme_selector()
        Kann das Stundengeläut-Theme für Festtage anpassen.
    """

    def __init__(self, striker: Striker):
        """
        Bereitet das Direktorium vor und impft alle automatischen
        Verbesserungen nach Bedarf ein.

        Parameters
        ----------
        striker : Striker
            Das Schlagwerk, dessen Funktion erweitert werden soll.
        """
        self.striker: Striker = striker
        self.settings: DirektoriumSettings = Settings().direktorium
        self.direktorium: TodayDirektorium = TodayDirektorium(
            kalender=self.settings.kalender, cache_dir=self.settings.cachedir)

        if self.settings.eastermute: self.striker.subscribe(self._mute_easter)
        if self.settings.antiphon is not None:
            self.striker.subscribe(self._marianic_antiphon)

        self.theme_modified: bool = False
        schedule.every().day.at('00:00').do(self._theme_selector)

    def _marianic_antiphon(
        self, melody: Melody, hours: int, quarters: int
    ) -> Melody:
        """Callback, das bei Bedarf eine marianische Antiphon anhängt."""
        h, q = self.settings.antiphon.split(':')
        if hours != int(h) or quarters != int(q) // 15: return melody

        season = self.direktorium.season()
        apath = self.settings.antiphon_ordinary
        if season == Season.CHRISTMAS:
            apath = self.settings.antiphon_christmas
        elif season == Season.LENT:
            apath = self.settings.antiphon_lent
        elif season == Season.EASTER:
            apath = self.settings.antiphon_easter
        antiphon = Melody.from_file(apath)
        antiphon.transpose = self.settings.antiphon_transpose
        antiphon.tempo = self.settings.antiphon_tempo

        return melody + antiphon

    def _mute_easter(
        self, melody: Melody, hours: int, quarters: int
    ) -> Melody:
        """Callback, das vor Ostern für Ruhe sorgt."""
        easter = self.direktorium.easter()
        if date.today() == easter - timedelta(days=1): return None
        if date.today() == easter - timedelta(days=2): return None
        return melody

    def _theme_selector(self) -> None:
        """Wählt ggf. nach Tagesrang ein anderes Theme aus."""
        event = self.direktorium.get()[0]
        rank = event.rank
        if rank == Rank.HOCHFEST and self.settings.theme_hochfest is not None:
            self.striker.theme = self.settings.theme_hochfest
            self.theme_modified = True
        elif rank == Rank.FEST and self.settings.theme_fest is not None:
            self.striker.theme = self.settings.theme_fest
            self.theme_modified = True
        elif rank == Rank.GEBOTEN and self.settings.theme_geboten is not None:
            self.striker.theme = self.settings.theme_geboten
            self.theme_modified = True
        elif rank == Rank.NICHTGEBOTEN and \
                self.settings.theme_nichtgeboten is not None:
            self.striker.theme = self.settings.theme_nichtgeboten
            self.theme_modified = True
        elif 'sonntag' in event.title.lower():
            self.striker.theme = self.settings.theme_sonntag
            self.theme_modified = True
        elif self.theme_modified:
            self.striker.theme = Settings().striker.theme
            self.theme_modified = False
