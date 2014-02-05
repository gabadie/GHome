#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')

from enocean.devices import Sensor
from trigger import Trigger, ThresholdTrigger, IntervalTrigger

import mongoengine

class TestTelegram:

    def __init__(self, value):
        self.value = value


class TestSensor(Sensor):
    _triggers = mongoengine.fields.ListField(mongoengine.fields.ReferenceField(Trigger), default=list)
    
    _old_value = 0

    def add_trigger(self, t):
        t.save()
        self._triggers.append(t)

    def process_telegram(self, telegram):
        for t in self._triggers:
            t.trigger(self._old_value, telegram.value, None)

        self._old_value = telegram.value


def test_add_trigger():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    s = TestSensor(device_id=131317, name='Test Sensor')
    s.add_trigger(ThresholdTrigger(name='Threshold0', min=10, max=30))
    s.add_trigger(IntervalTrigger(name='Interval0', min=10, max=30))
    s.add_trigger(ThresholdTrigger(name='Threshold1', min=6, max=18))

    assert "Threshold0.underflow" in s.events
    assert "Threshold0.overflow" in s.events
    assert "Interval0.enterInFromAbove" in s.events
    assert "Interval0.enterInFromBelow" in s.events
    assert "Interval0.aboveInterval" in s.events
    assert "Interval0.belowInterval" in s.events
    assert "Threshold1.underflow" in s.events
    assert "Threshold1.overflow" in s.events


def test_threshold_trigger():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    s = TestSensor(device_id=131317, name='Test Sensor')
    s.add_trigger(ThresholdTrigger(name='Threshold0', min=10, max=30))

    s.process_telegram(TestTelegram(11))

    s.process_telegram(TestTelegram(31))
    s.process_telegram(TestTelegram(1))


def test_interval_trigger():
    pass


if __name__ == "__main__":
    test_add_trigger()

    test_threshold_trigger()

    test_interval_trigger()
