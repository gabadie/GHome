#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import core
import devices


class ThermometerReading(core.Reading):
    temperature = mongoengine.FloatField(required=True)
    humidity = mongoengine.FloatField(required=True)


def from_thermometer(thermometer, data_bytes):
    return ThermometerReading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)
