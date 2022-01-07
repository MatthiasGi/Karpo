#!/usr/bin/env python3
import time

from lib import Carillon, Jukebox, MqttClient


if __name__ == '__main__':
    c = Carillon()
    m = MqttClient()
    j = Jukebox(c, m)

    while True:
        time.sleep(0.1)
