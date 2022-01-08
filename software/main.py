#!/usr/bin/env python3
import time

from lib import AngelusPlayer, Carillon, DirektoriumProxy, Striker, Nightmuter


if __name__ == '__main__':
    c = Carillon()
    s = Striker(c)
    Nightmuter(s)
    DirektoriumProxy(s)
    AngelusPlayer(s)

    while True:
        time.sleep(0.1)
