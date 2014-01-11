#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import components
import devices


class ThermometerReading(components.Reading):
    temperature = mongoengine.FloatField(required=True)
    humidity = mongoengine.FloatField(required=True)


def from_thermometer(thermometer, data_pytes):
    return ThermometerReading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)


if __name__ == "__main__":
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = from_thermometer(None, data_bytes)

    assert reading.humidity == 52.8
    assert reading.temperature == 24.48

    print "Tests passed !"
