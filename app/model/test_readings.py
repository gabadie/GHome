#!/usr/bin/env python
# -*- coding: utf-8 -*-

import readings


def test_thermometer():
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = readings.from_thermometer(None, data_bytes)

    assert reading.humidity == 52.8
    assert reading.temperature == 24.48

    return True

if __name__ == "__main__":
    test_thermometer()
    print 'all OK'
