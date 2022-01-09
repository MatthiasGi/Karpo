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
Im Folgenden wird die Installation im üblichsten Use-Case beschrieben: Einem
RaspberryPi-Server, der auch über Inputs für eine Klingel verfügt.

1. Einrichten der microSD-Karte: Es empfiehlt sich, eine Standard Installation
   mit Raspberry Pi OS vorzunehmen. Dort ist ein Desktop vorhanden. Der
   [Raspberry Pi Imager](https://www.raspberrypi.com/software/) verfügt über ein
   verstecktes Menü, dass sich über <kbd>Ctrl</kbd> + <kbd>Shift</kbd> +
   <kbd>X</kbd> erreichen lässt. Dort können ein Hostname (etwa `karpo.local`)
   gewählt, SSH aktiviert, WLAN vorkonfiguriert, die Spracheinstellungen
   festgelegt und der Einrichtungsassistent übersprungen werden.
2. microSD-Karte in den Pi (etwa RPi Zero) einlegen, starten, warten und eine
   Verbindung über SSH herstellen.
3. VNC über `sudo raspi-config` aktivieren: Interface Options / VNC
4. Updates einspielen:
   `sudo apt update && sudo apt -y upgrade && sudo apt -y dist-upgrade`
5. Installieren der Audiokarte (abhängig vom konkreten DAC, in meinem Falle des
   Pimoroni pHAT DAC[^pimoroni] etwa über:
   `curl https://get.pimoroni.com/phatdac | bash`)
6. GrandOrgue installieren[^grandorgue install]:
```
echo 'deb http://download.opensuse.org/repositories/home:/e9925248:/grandorgue/Raspbian_10/ /' | sudo tee /etc/apt/sources.list.d/home:e9925248:grandorgue.list
curl -fsSL https://download.opensuse.org/repositories/home:e9925248:grandorgue/Raspbian_10/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/home_e9925248_grandorgue.gpg > /dev/null
sudo apt update
sudo apt -y install grandorgue
```
7. Abhängigkeiten für die Pythonskripts installieren: `pip install pipenv`
8. Computer neustarten.

### Konfiguration
Nach dem Neustart kann die Einrichtung fortgesetzt werden.

1. Neue Verbindung über SSH aufbauen.
2. Testen der Audiokarte durch Anschluss eines Lautsprechers und
   `sudo speaker-test -l5 -c2 -t wav`
3. Dieses Repository runterladen: `git clone https://github.com/MatthiasGi/Karpo.git`
4. Weitere Konfiguration über VNC-Verbindung.
5. GrandOrgue starten und konfigurieren:
   1. Carillon-Orgel `~/Karpo/carillon/carillon.organ` öffnen.
   2. Rechtsklick auf Manual, dort folgende Einstellungen vornehmen:
      - Device: Any device
      - Event: 9x Note
      - Channel: Any channel
      - Lowest key: 0
      - Highest key: 127
      - Lowest velocity: 1
      - Highest velocity: 127
   3. OK, dann im Hauptfenstermenü auf Panel > Coupler manuals and volume. Dort
      Rechtsklick auf den Master-Schweller und folgende Einstellungen vornehmen:
      - Device: Any device
      - Event: Bx Controller
      - Channel: Any channel
      - Controller-No: 7
      - Lower limit: 0
      - Upper limit: 127
   4. OK, dann Panel schließen und Lautstärke fein abstimmen: Glocke anschlagen
      und im Haupfenster Lautstärke hochregeln, bis in Ordnung.
   5. Im Hauptfenstermenü File > Save
6. VNC-Verbindung schließen, da nicht mehr nötig. Zurück zu SSH.

Was hier noch fehlt:
* Anschluss des Raspberry Pis
* Einstellungsdatei (auf Basis der `config.example.json`)
* Autostart des Runscripts (folgt!)


[^pimoroni]: https://learn.pimoroni.com/article/raspberry-pi-phat-dac-install
[^grandorgue install]: https://software.opensuse.org/download/package?project=home:e9925248:grandorgue&package=grandorgue


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

[^sonimusicae]: Das Carillon ist der Seite
  http://sonimusicae.free.fr/carillondegand-en.html entnommen.
[^grandorgue]: https://github.com/GrandOrgue/grandorgue

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

#### Angelus
Die Klasse `lib.angelusplayer.AngelusPlayer` ist in der Lage, zu vorbestimmten
Zeiten einen Angelus zu spielen. Unter den Einstellungen `angelus` findet sich
insbesondere der Parameter `times`, der dann Kommagetrennt Zeiten für den
Angelus erwartet, also etwa `"06:00,12:00,18:00"`. Der Angelus funktioniert
allerdings nur in **Zusammenhang mit dem Stundengeläut**. Ist das also stumm
(wegen etwa der Nachtabschaltung), so kommt es auch zu keinem Angelusgeläut. Die
Angelusmelodie wird mittels `path` hinterlegt und lässt sich auch Transponieren
(`transpose`) bzw. im Tempo anpassen (`tempo`).


## Direktorium
Die aus Vorprojekten entlehnte Bibliothek `lib.direktorium` macht Angaben über
den liturgischen Kalender und basiert auf der API von Hatto v. Hatzfeld
SDB[^lk-api].

[^lk-api]: Der liturgische Kalender von eucharistiefeier.de ist erreichbar
unter: http://www.eucharistiefeier.de/lk/. Die Server stellen dafür die
Salesianer Don Boscos zur Verfügung.

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


### MQTT-Controller
Der `lib.mqttcontroller.MqttController` bietet weiterhin die Möglichkeit, einige
globale Einstellungen über MQTT vorzunehmen. Im Einzelnen sind das:
* `control/volume/get`: Teilt die eingestellte Lautstärke unter `control/volume`
  mit.
* `control/volume/set`: Setzt die Lautstärke und teilt sie wie oben mit.
* `control/stop`: Stoppt alles, was gerade abgespielt wird.
* `control/theme/get`: Teilt unter `control/theme` das eingestellte
  Schlagwerk-Theme mit.
* `control/theme/list/get`: Listet unter `control/theme/list` alle verfügbaren
  Themes auf.
* `control/theme/set`: Stellt das Theme ein und teilt es wie oben mit.
