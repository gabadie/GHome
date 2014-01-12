#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

import model
import devices


def test_mongoengine():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    thermometer = devices.Thermometer(device_id="Hello")

    assert not thermometer in model.core.Device.objects

    thermometer.save()

    assert thermometer in model.core.Device.objects
    assert thermometer in model.core.Device.objects(device_id="Hello")
    assert not thermometer in model.core.Device.objects(device_id="World")

    thermometerValue = model.devices.Thermometer.Reading(device=thermometer, temperature=0.0, humidity=0.0)
    thermometerValue.save()

    assert thermometerValue in model.devices.Thermometer.Reading.objects(device=thermometer)

def test_thermometer():
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = devices.Thermometer.reading_from_data_bytes(None, data_bytes)

    assert reading.humidity == 52.8
    assert reading.temperature == 24.48

if __name__ == "__main__":
    test_mongoengine()
    test_thermometer()
