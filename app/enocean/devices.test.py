#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

from enocean.devices import Sensor, Thermometer, Lamp, Switch, WindowContact, LightMovementSensor
from model.devices import Device, Temperature, Humidity
from model.trigger import ThresholdTrigger


def test_mongoengine():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    thermometer = Thermometer(device_id=1, ignored=False)

    assert not thermometer in Device.objects

    thermometer.save()

    assert thermometer in Sensor.objects
    assert thermometer in Sensor.objects(device_id=1, ignored=False)
    assert not thermometer in Sensor.objects(device_id=2, ignored=False)

    temp_reading = Temperature(device=thermometer, value=1.337)
    humidity_reading = Humidity(device=thermometer, value=4.242)

    temp_reading.save()
    humidity_reading.save()

    assert temp_reading == Temperature.objects.get(device=thermometer)
    assert humidity_reading == Humidity.objects.get(device=thermometer)

def test_last_reading():
    db = mongoengine.connect('ghome_enocean_test')
    db.drop_database('ghome_enocean_test')

    thermometer = Thermometer(device_id=442)
    thermometer.save()

    tel = thermometer.generate_telegram(sensor_id=442, temperature=24.48, humidity=52.8)
    thermometer.process_telegram(tel, None)

    assert 'Temperature' in thermometer.last_readings
    assert 'Humidity' in thermometer.last_readings

def test_thermometer():
    thermometer = Thermometer(device_id="50")

    # Test 1
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    validity, temperature, humidity = thermometer.parse_readings(data_bytes, None)

    assert humidity.value == 52.8
    assert temperature.value == 24.48

    # Test 2
    thermometer = Thermometer(device_id=403, ignored=False)
    thermometer.save()
    t = thermometer.generate_telegram(sensor_id=407, temperature=24.48, humidity=52.8)
    thermometer.process_telegram(t, None)
    validity, temperature, humidity = thermometer.parse_readings(t.data_bytes, None)
    print temperature
    assert temperature.value == 24.48
    assert humidity.value == 52.8

def test_lamp():
    lamp = Lamp(device_id=404)
    assert not lamp.activated
    lamp.callback_turn_on(None)
    assert lamp.activated
    lamp.save()

    assert 'callback_turn_on' in lamp.callbacks
    assert 'callback_turn_off' in lamp.callbacks
    assert 'callback_toggle' in lamp.callbacks

def test_switch():
    switch = Switch(device_id=405, ignored=False)
    assert not switch.top_right
    assert not switch.bottom_right
    assert not switch.top_left
    assert not switch.bottom_left
    switch.save()
    t = switch.generate_telegram(sensor_id=405, side=Switch.RIGHT, direction=Switch.TOP, pressed=True)
    switch.process_telegram(t, None)
    assert switch.top_right
    assert not switch.bottom_right
    assert not switch.top_left
    assert not switch.bottom_left

def test_window_contactor():
    wc = WindowContact(device_id=406, ignored=False, open=False)
    wc.save()
    assert not wc.open
    t = wc.generate_telegram(sensor_id=406, open=True)
    wc.process_telegram(t, None)
    reading = WindowContact.parse_readings(wc, t.data_bytes, None)
    assert reading.value == True

def test_light_movement_sensor():
    lms = LightMovementSensor(device_id=407, ignored=False)
    lms.save()
    t = lms.generate_telegram(sensor_id=407, voltage=4.5, brightness=48, movement=True)
    lms.process_telegram(t, None)
    voltage, brightness, movement = lms.parse_readings(t.data_bytes, None)

    assert voltage.value == 4.5
    assert brightness.value == 48
    assert movement.value

def test_has_events():
    thermometer = Thermometer(device_id=404)
    switch = Switch(device_id=405, ignored=False)
    wc = WindowContact(device_id=406, ignored=False, open=False)
    lms = LightMovementSensor(device_id=407, ignored=False)

    print "Thermometer events : {} ".format(thermometer.events)
    print "Switch events : {} ".format(switch.events)
    print "Window contact events : {} ".format(wc.events)
    print "Light sensor events : {} ".format(lms.events)

    thermometer.temperature_triggers.append(ThresholdTrigger(name="Threshold0", min=10, max=45))
    thermometer.temperature_triggers.append(ThresholdTrigger(name="Threshold1", min=46, max=50))
    print "Thermometer events : {} ".format(thermometer.events)

    lms.voltage_triggers.append(ThresholdTrigger(name="VoltThreshold", min=10, max=45))
    lms.brightness_triggers.append(ThresholdTrigger(name="BrightThreshold", min=10, max=45))
    print "Light sensor events : {} ".format(lms.events)

    assert 'Threshold0.underflow' in thermometer.events
    assert 'Threshold0.overflow'  in thermometer.events
    assert 'Threshold1.underflow' in thermometer.events
    assert 'Threshold1.overflow'  in thermometer.events

    assert 'onclick_bottom_left'  in switch.events
    assert 'onclick_bottom_right' in switch.events
    assert 'onclick_top_left'  in switch.events
    assert 'onclick_top_right' in switch.events

    assert 'on_opened' in wc.events
    assert 'on_closed' in wc.events

    assert 'on_moved' in lms.events
    assert 'VoltThreshold.underflow' in lms.events
    assert 'VoltThreshold.overflow'  in lms.events
    assert 'BrightThreshold.underflow' in lms.events
    assert 'BrightThreshold.overflow'  in lms.events


if __name__ == "__main__":
    test_mongoengine()
    test_last_reading()
    test_thermometer()
    test_lamp()
    test_switch()
    test_window_contactor()
    test_light_movement_sensor()
    test_has_events()
    print "Tests passed !"
