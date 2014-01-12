#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

import model
import devices


if __name__ == '__main__':
    db = mongoengine.connect('test')
    db.drop_database('ghome_model_tests')

    thermometer = devices.Thermometer(device_id="Hello")

    assert not thermometer in model.core.Device.objects

    thermometer.save()

    assert thermometer in model.core.Device.objects
    assert thermometer in model.core.Device.objects(device_id="Hello")
    assert not thermometer in model.core.Device.objects(device_id="World")

    thermometerValue = model.devices.Thermometer.Reading(device=thermometer, temperature=0.0, humidity=0.0)
    thermometerValue.save()

    assert thermometerValue in model.devices.Thermometer.Reading.objects(device=thermometer)

