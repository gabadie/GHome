#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import components
import devices

db = mongoengine.connect('ghome_model_tests')
db.drop_database('ghome_model_tests')

thermometer = devices.Thermometer(device_id="Hello")

assert not thermometer in components.Device.objects

thermometer.save()

assert thermometer in components.Device.objects
assert thermometer in components.Device.objects(device_id="Hello")
assert not thermometer in components.Device.objects(device_id="World")

