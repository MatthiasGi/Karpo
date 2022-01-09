#!/usr/bin/env python3
import time

from lib import AngelusPlayer, Carillon, DirektoriumProxy, Jukebox, \
    MqttClient, MqttController, Nightmuter, Striker


if __name__ == '__main__':
    c = Carillon()
    s = Striker(c)
    Nightmuter(s)
    DirektoriumProxy(s)
    AngelusPlayer(s)

    m = MqttClient()
    if m is not None:
        Jukebox(c, m)
        MqttController(s, m)

    while True:
        time.sleep(0.1)
