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

    thermometer = devices.Thermometer(device_id=1, ignored=False)

    assert not thermometer in model.devices.Device.objects

    thermometer.save()

    assert thermometer in model.devices.Sensor.objects
    assert thermometer in model.devices.Sensor.objects(device_id=1, ignored=False)
    assert not thermometer in model.devices.Sensor.objects(device_id=2, ignored=False)

    thermometerValue = model.devices.Thermometer.Reading(device=thermometer, temperature=0.0, humidity=0.0)
    thermometerValue.save()

    assert thermometerValue in model.devices.Thermometer.Reading.objects(device=thermometer)

def test_thermometer():
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = devices.Thermometer.reading_from_data_bytes(None, data_bytes)
    assert reading.humidity == 52.8
    assert reading.temperature == 24.48
    
    thermometer = devices.Thermometer(device_id=403, ignored=False)
    thermometer.save()
    t = thermometer.generate_telegram(sensor_id=407, temperature=24.48, humidity=52.8)
    thermometer.process_telegram(t, None)
    reading = devices.Thermometer.reading_from_data_bytes(thermometer, t.data_bytes)
    assert reading.temperature == 24.48
    assert reading.humidity == 52.8

def test_lamp():
    lamp = devices.Lamp(device_id=404)
    assert not lamp.turned_on
    lamp.activate(sensor=None)
    assert lamp.turned_on
    lamp.save()
    
def test_switch():
    switch = devices.Switch(device_id=405, ignored=False)
    assert not switch.top_right
    assert not switch.bottom_right
    assert not switch.top_left
    assert not switch.bottom_left
    switch.save()
    t = switch.generate_telegram(sensor_id=405, side=devices.Switch.RIGHT, direction=devices.Switch.TOP, pressed=True)
    switch.process_telegram(t, None)
    assert switch.top_right
    assert not switch.bottom_right
    assert not switch.top_left
    assert not switch.bottom_left
    
def test_window_contactor():
    wc = devices.WindowContact(device_id=406, ignored=False, open=False)
    wc.save()
    assert not wc.open
    t = wc.generate_telegram(sensor_id=406, open=True)
    wc.process_telegram(t, None)
    reading = devices.WindowContact.reading_from_data_bytes(wc, t.data_bytes)
    assert reading.open == True
    
def test_light_movement_sensor():
    lms = devices.LightMovementSensor(device_id=407, ignored=False)
    lms.save()
    t = lms.generate_telegram(sensor_id=407, voltage=12.5, brightness=48, movement=True)
    print t.data_bytes[0]
    lms.process_telegram(t, None)
    reading = devices.LightMovementSensor.reading_from_data_bytes(lms, t.data_bytes)
    print reading.voltage
    assert reading.voltage == 12.5
    assert reading.brightness == 48
    assert reading.movement

if __name__ == "__main__":
    test_mongoengine()
    test_thermometer()
    test_lamp()
    test_switch()
    test_window_contactor()
    test_light_movement_sensor()
    