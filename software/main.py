#!/usr/bin/env python3
import time

from lib import AngelusPlayer, Carillon, FestivePlayer, GpioBell, \
    DirektoriumProxy, Jukebox, MqttClient, MqttController, Nightmuter, Striker


if __name__ == '__main__':
    print('\n\n------------------------------------------------------------\n')
    print('Hello world! This is Karpo speaking!')
    c = Carillon()
    s = Striker(c)
    Nightmuter(s)
    DirektoriumProxy(s)
    AngelusPlayer(s)
    FestivePlayer(s)

    m = MqttClient()
    if m.client is not None:
        Jukebox(c, m)
        MqttController(s, m)

    GpioBell(c, m)

    print('Vorbereitungen abgeschlossen, mache mich an das unendliche Warten…')

    while True:
        time.sleep(0.1)
