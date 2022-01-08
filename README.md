# Karpo

> Die Horen sind in der griechischen Mythologie die Göttinnen, die das geregelte
> Leben überwachen. Sie sollen an einem Webstuhl das Leben eines Menschen
> bestimmt und gewebt haben. Das griechische Wort hora bedeutet „Zeit“ oder
> „Zeitabschnitt”; es kann ein Jahr, eine Jahreszeit, eine Tageszeit oder eine
> Stunde bezeichnen.
> Karpo ist eine der drei Horen. Karpo wird mit Reife, Ernte und Herbst
> assoziiert.
>
> — *Aus Wikipedia (Horen/Karpo)*

Karpo soll ein ausgewachsenes und „reifes“ Stundengeläut sein. Im Herzen steht
dafür ein virtuelles Carillon, das regelmäßig eine Zeit anschlägt. Modular darum
gruppieren sich verschiedene Funktionen zur Erweiterung.


## Installation
Hier folgen zeitnah einige Sätze zum Ablauf der Installation. Einige Stichpunkte
bereits vorab:
* Installation von GrandOrgue
* Öffnen der Orgeldatei und MIDI-Einstellungen für Töne und Lautstärke
* Vorbereitung mittels `pipenv`
* Einstellungsdatei (auf Basis der `config.example.json`)
* Autostart des Runscripts (folgt!)
* Anschluss im Falle eines Raspberry Pis


## Einstellungen
Globale Einstellungen werden in der Klasse `lib.settings.Settings` organisiert.
Sie versucht aus einer `config.json` zu lesen, für deren Startpunkt gerne
`config.example.json` übernommen werden kann. Einzelne Relevante Einstellungen
werden weiter unten in den entsprechenden Klassen beschrieben.


## Carillon
Im Unterordner `carillon` befindet sich dazu eine Orgeldefinitionsdatei. Diese
basiert auf den Arbeiten von Soni Musicae[^sonimusicae] und ist etwas um
fehlende Töne erweitert worden. Sie lässt sich in GrandOrgue[^grandorgue]
öffnen. In dieser Software lassen sich nun MIDI-Signale einspielen, die in
Glockenschläge umgewandelt werden. Genau dieses Verhalten macht sich Karpo
zunutze, indem es zur passenden Zeit diese Glockenschläge auslöst.

Die Software implementiert `lib.carillon.Carillon` als Klasse, die die
Kommunikation mit GrandOrgue abstrahiert. Ferner ist dort explizit die
Einstellung der Lautstärke möglich. Diese wird als Control-Change-Message an den
Controller 7 gesendet, der per MIDI-Konvention vornehmlich für Lautstärke zu
verwenden ist.


### Melodien
Kern der Wiedergabe auf dem Carillon ist eine Melodie, wie sie durch
`lib.melody.Melody` modelliert ist. Factory-Methoden helfen beim Erstellen
dieser Liste an MIDI-Messages. Das Objekt selber ermöglicht Tempoänderung und
Transponierung der voreingestellten Melodie.


### Schlagwerk
Die Klasse `lib.striker.Striker` regelt das regelmäßige Schlagen auf dem
Carillon. In den Einstellungen kann neben der Priorität `priority` auch ein sog.
`theme` festgelegt werden. In der `basefolder` wird ein Ordner mit dem Namen des
gewählten `themes` gesucht. In ihm können sich folgende Dateien befinden:
* `q1.mid`: Wird zur ersten Viertelstunde gespielt.
* `q2.mid`: Wird zur zweiten Viertelstunde gespielt.
* `q3.mid`: Wird zur dritten Viertelstunde gespielt.
* `q4.mid`: Wird zur vierten Viertelstunde gespielt.
* `h.mid`: Wird bei der vierten Viertelstunde im Anschluss bis zu 12-mal
  wiederholt (entsprechend der Stundenzahl).
Fehlt eine der Dateien, wird sie einfach nicht wiedergegeben.

Es ist ferner auch möglich, einzelne Themes in den Einstellungen anzupassen: In
einem Untereinstellungsdictionary `themes` kann für jedes Theme optional ein
eigenes Dictionary angelegt werden. Dort sind Einstellungen zu Transponierung
und Tempo für das spezifische Theme möglich.

Folgende Themes sind definiert:
* `default`: Ein einfaches Schlagwerk aus je einem Ton für Viertelstunde und
  Stunde.
* `mehrerau`: Ein Geläut, dass dem der Territorialabtei Wettingen-Mehrerau
  entlehnt ist. Zur Viertelstunde läuten insgesamt drei Glocken (*Engel* A2#,
  *Bernhard* G2#, *Apostel* F2#), zur vollen Stunde eine Glocke (*Trinitatis*
  A1#). Das Abteigeläut verfügt ferner über zwei weitere – hier ungenutzte –
  Glocken (*Josef* D2#, *Maria* C2#).
* `westminster`: Der klassische Westminster-Schlag.

Ferner können einzelne Observer angehängt werden, die das Verhalten des
Schlagwerks anpassen.

#### Nachtabschaltung
Die Klasse `lib.nightmuter.Nightmuter` stellt sicher, dass das Schlagwerk nicht
in der Nacht auslöst. Dazu wird in den Einstellungen zum Schlagwerk `striker`
eine Abschaltungsstartzeit `nightmuter_start` und Endzeit `nightmuter_end`
angegeben.

[^sonimusicae]: Das Carillon ist der Seite
  http://sonimusicae.free.fr/carillondegand-en.html entnommen.
[^grandorgue]: https://github.com/GrandOrgue/grandorgue


## Direktorium
Die aus Vorprojekten entlehnte Bibliothek `lib.direktorium` macht Angaben über
den liturgischen Kalender und basiert auf der API von Hatto v. Hatzfeld
SDB[^lk-api].

Dadurch kann das Geläut auf liturgische Feste reagieren. Die einzelnen Aspekte
lassen sich in der Einstellungsdatei unter dem Punkt `direktorium` steuern. Im
Einzelnen sind das folgende Möglichkeiten:
* `cachedir`: Pfad zum Ordner, indem die liturgischen Informationen
  zwischengespeichert werden können.
* `eastermute`: Ob Karfreitag und Karsamstag das Geläut schweigen soll.
* `kalender`: Bezeichnung des zu verwendenden Lokalkalenders[^kalender].
* `theme_nichtgeboten`: Ggf. alternatives Geläut-Theme für nichtgebotene
  Gedenktage.
* `theme_geboten`: Ggf. alternatives Geläut-Theme für gebotene Gedenktage.
* `theme_fest`: Ggf. alternatives Geläut-Theme für Feste.
* `theme_hochfest`: Ggf. alternatives Geläut-Theme für Hochfeste.
* `antiphon`: Angabe zur Zeit, an deren Geläutanschluss sich eine Marianische
  Antiphon anschließen soll.
* `antiphon_christmas`: Pfad zur Antiphon für die Weihnachtszeit (Alma
  redemptoris mater).
* `antiphon_lent`: Pfad zur Antiphon für die Fastenzeit (Ave Regina caelorum).
* `antiphon_easter`: Pfad zur Antiphon für die Osterzeit (Regina caeli laetare).
* `antiphon_ordinary`: Pfad zur Antiphon für die nichtgeprägten Zeiten (Salve
  Regina).
* `antiphon_transpose`: Globale Option zur Transponierung der Antiphonen.
* `antiphon_tempo`: Globale Option zur Tempoanpassung der Antiphonen.

[^lk-api]: Der liturgische Kalender von eucharistiefeier.de ist erreichbar
unter: http://www.eucharistiefeier.de/lk/. Die Server stellen dafür die
Salesianer Don Boscos zur Verfügung.
[^kalender]: Die verfügbaren Kalender sind unter
http://www.eucharistiefeier.de/lk/teilkirchen.php einsehbar.


## MQTT
Der MQTT-Client erlaubt es, das Schlaggeläut etwa in das SmartHome zu
integrieren. Einzelne Module können andocken, um auf Nachrichten zu reagieren.
Für die Einstellungen ist in der Sektion `mqtt` die Vergabe einer `id`, des
`server` und `port` sicherlich hilfreich. Ist der `server` mit `null` angegeben,
wird MQTT für den Betrieb ausgespart. Ein `basetopic` wird (gefolgt von einem
Slash `/`) allen Nachrichtentopics vorangestellt. Etwa für die Verwendung in
Verbindung mit HomeAssisstant ist eine Authentifizierung zwingend erforderlich.
Benutzername und Passwort können daher ebenfalls hinterlegt werden. Ein User
`null` verhindert einen Authentifizierungsversuch.


### Jukebox
Ein simples MQTT-Modul erlaubt die Wiedergabe beliebiger Melodien. Von ihr
gewählte Lieder können in den Einstellungen eine Priorität eingeräumt werden,
die Lieder werden in einer zu spezifizierenden `basefolder` gesucht. Als
MQTT-Topics stehen zur Auswahl:

* `jukebox/play`: Spielt eine Melodie aus dem Liederordner mit dem
  entsprechenden Namen in der Payload.
* `jukebox/stop`: Unterbricht die Wiedergabe.
* `jukebox/list/get`: Gibt eine Liste aller verfügbaren Lieder auf
  `jukebox/list` zurück.
* `jukebox/transpose/set`: Erlaubt es, die Transponierung folgender Lieder
  festzulegen und bestätigt die Eingabe auf `jukebox/transpose`.
* `jukebox/transpose/get`: Gibt die aktuelle Transponierung auf
  `jukebox/transpose` zurück.
