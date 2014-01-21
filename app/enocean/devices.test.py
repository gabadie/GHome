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

    assert not thermometer in model.devices.Device.objects

    thermometer.save()

    assert thermometer in model.devices.Device.objects
    assert thermometer in model.devices.Device.objects(device_id="Hello")
    assert not thermometer in model.devices.Device.objects(device_id="World")

    temp_reading = model.devices.Temperature(device=thermometer, value=1.337)
    humidity_reading = model.devices.Humidity(device=thermometer, value=4.242)

    temp_reading.save()
    humidity_reading.save()

    assert temp_reading in model.devices.Temperature.objects(device=thermometer)
    assert humidity_reading in model.devices.Humidity.objects(device=thermometer)

def test_thermometer():
    thermometer = devices.Thermometer(device_id="test_thermometer_1")

    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    temperature, humidity = thermometer.parse_readings(data_bytes)

    assert humidity.value == 52.8
    assert temperature.value == 24.48

def test_lamp():
    lamp = devices.Lamp(device_id='lamp101')
    assert not lamp.turned_on
    lamp.activate(sensor=None)
    assert lamp.turned_on

def test_switch_lamp():
    lamp = devices.Lamp(device_id='lamp202')
    other_lamp = devices.Lamp(device_id='lamp303', turned_on=True)

    switch = devices.Switch(device_id='switch202', actuators=[lamp, other_lamp])

    assert not lamp.turned_on
    assert other_lamp.turned_on

    switch.activated()

    assert lamp.turned_on
    assert not other_lamp.turned_on


if __name__ == "__main__":
    test_mongoengine()
    test_thermometer()
    test_lamp()
    test_switch_lamp()
