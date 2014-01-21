#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

import model
import enocean.devices as devices


def test_mongoengine():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    thermometer = devices.Thermometer(device_id=1, ignored=False)

    assert not thermometer in model.devices.Device.objects

    thermometer.save()

    assert thermometer in model.devices.Sensor.objects
    assert thermometer in model.devices.Sensor.objects(device_id=1, ignored=False)
    assert not thermometer in model.devices.Sensor.objects(device_id=2, ignored=False)

    temp_reading = model.devices.Temperature(device=thermometer, value=1.337)
    humidity_reading = model.devices.Humidity(device=thermometer, value=4.242)

    temp_reading.save()
    humidity_reading.save()

    assert temp_reading in model.devices.Temperature.objects(device=thermometer)
    assert humidity_reading in model.devices.Humidity.objects(device=thermometer)

def test_thermometer():
    thermometer = devices.Thermometer(device_id="test_thermometer_1")

    # Test 1
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    temperature, humidity = thermometer.parse_readings(data_bytes)

    assert humidity.value == 52.8
    assert temperature.value == 24.48

    # Test 2
    thermometer = devices.Thermometer(device_id=403, ignored=False)
    thermometer.save()
    t = thermometer.generate_telegram(sensor_id=407, temperature=24.48, humidity=52.8)
    thermometer.process_telegram(t, None)
    temperature, humidity = thermometer.parse_readings(t.data_bytes)
    assert temperature.value == 24.48
    assert humidity.value == 52.8

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
    reading = devices.WindowContact.parse_readings(wc, t.data_bytes)
    assert reading.value == True

def test_light_movement_sensor():
    lms = devices.LightMovementSensor(device_id=407, ignored=False)
    lms.save()
    t = lms.generate_telegram(sensor_id=407, voltage=4.5, brightness=48, movement=True)
    lms.process_telegram(t, None)
    voltage, brightness, movement = lms.parse_readings(t.data_bytes)

    assert voltage.value == 4.5
    assert brightness.value == 48
    assert movement.value

if __name__ == "__main__":
    test_mongoengine()
    test_thermometer()
    test_lamp()
    test_switch()
    test_window_contactor()
    test_light_movement_sensor()
    print "Tests passed !"
