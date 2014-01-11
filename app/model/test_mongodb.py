#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import core
import devices

db = mongoengine.connect('ghome_model_tests')
db.drop_database('ghome_model_tests')

thermometer = devices.Thermometer(device_id="Hello")

assert not thermometer in core.Device.objects

thermometer.save()

assert thermometer in core.Device.objects
assert thermometer in core.Device.objects(device_id="Hello")
assert not thermometer in core.Device.objects(device_id="World")

