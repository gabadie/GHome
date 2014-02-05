#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

from enocean.devices import Sensor
from event import Trigger, ThresholdTrigger

import mongoengine

db = mongoengine.connect('ghome_enocean_test')
db.drop_database('ghome_enocean_test')

class DefSensor(Sensor):
    _triggers = mongoengine.fields.ListField(mongoengine.fields.ReferenceField(Trigger), default=list)

    def add_trigger(self, t):
        t.save()
        self._triggers.append(t)


s = DefSensor(device_id=131317, name='Lol Sensor')
t = ThresholdTrigger(name='lol', min=10, max=30)
s.add_trigger(t)

print s.events
