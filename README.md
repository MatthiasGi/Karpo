# Karpo

> Die Horen sind in der griechischen Mythologie die Göttinnen, die das geregelte
> Leben überwachen. Sie sollen an einem Webstuhl das Leben eines Menschen
> bestimmt und gewebt haben. Das griechische Wort hora bedeutet „Zeit“ oder
> „Zeitabschnitt”; es kann ein Jahr, eine Jahreszeit, eine Tageszeit oder eine
> Stunde bezeichnen.
> Karpo ist eine der drei Horen. Karpo wird mit Reife, Ernte und Herbst
> assoziiert.
> — *Aus Wikipedia (Horen/Karpo)*

Karpo soll ein ausgewachsenes und „reifes“ Stundengeläut sein. Im Herzen steht
dafür ein virtuelles Carillon, das regelmäßig eine Zeit anschlägt. Modular darum
gruppieren sich verschiedene Funktionen zur Erweiterung.

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
