#!/usr/bin/env python3
import time

from lib import Carillon, Striker


if __name__ == '__main__':
    c = Carillon()
    s = Striker(c)

    while True:
        time.sleep(0.1)
