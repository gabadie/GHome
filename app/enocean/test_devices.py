#!/usr/bin/env python
# -*- coding: utf-8 -*-

import devices


def test_thermometer():
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = devices.Thermometer.reading_from_data_bytes(None, data_bytes)

    assert reading.humidity == 52.8
    assert reading.temperature == 24.48

    return True

if __name__ == "__main__":
    test_thermometer()
    print 'all OK'
