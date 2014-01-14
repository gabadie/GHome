#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import devices

db = mongoengine.connect('ghome_model_tests')
db.drop_database('ghome_model_tests')

thermometer = devices.Thermometer(device_id="Hello")

assert not thermometer in devices.Device.objects

thermometer.save()

assert thermometer in devices.Device.objects
assert thermometer in devices.Device.objects(device_id="Hello")
assert not thermometer in devices.Device.objects(device_id="World")

thermometerValue = devices.Thermometer.Reading(device=thermometer, temperature=0.0, humidity=0.0)
thermometerValue.save()

assert thermometerValue in devices.Thermometer.Reading.objects(device=thermometer)
