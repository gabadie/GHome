#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import components
import devices

db = mongoengine.connect('ghome_model_tests')
db.drop_database('ghome_model_tests')

thermometer = devices.Thermometer(device_id="Hello")
thermometer.save()

for f in components.Device.objects():
    print f.device_id

