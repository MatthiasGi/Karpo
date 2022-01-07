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

[^sonimusicae]: Das Carillon ist der Seite
  http://sonimusicae.free.fr/carillondegand-en.html entnommen.
[^grandorgue]: https://github.com/GrandOrgue/grandorgue
