#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

from telegram import Telegram
import model.devices
import logger


class Sensor(model.devices.Sensor):

    ignored = mongoengine.BooleanField(default=True)

    def process_telegram(self, telegram, server):
        raise NotImplementedError

# Sensors
class Thermometer(Sensor, model.devices.Thermometer):

    def parse_readings(thermometer, data_bytes):
        temperature = data_bytes[2] * 40 / 250.0
        humidity = data_bytes[1] * 100 / 250.0
        temp_r = model.devices.Temperature(device=thermometer, value=temperature)
        humidity_r = model.devices.Humidity(device=thermometer, value=humidity)

        logger.info("EnOcean thermometer reading: Temperature={}°C, Humidity={}%".format(temperature, humidity))

        return temp_r, humidity_r


    def process_telegram(self, telegram, server):
        temperature, humidity = self.parse_readings(self, telegram.data_bytes)

        temperature.save()
        humidity.save()

class Switch(Sensor, model.devices.Switch):

    def parse_readings(self, data_bytes):
        return model.devices.SwitchState(device=self, value=self.on)

    def process_telegram(self, telegram, server):
        self.on = not self.on
        switch_state = self.parse_readings(self, telegram.data_bytes)

        switch_state.save()
        self.save()

        self.activated()
        logger.info("EnOcean switch #{} activated".format(self.device_id))


class WindowContact(Sensor, model.devices.WindowContact):

    def parse_readings(self, data_bytes):
        self.open  = (self.data_bytes[3] & 0x01) == 0

        # TODO : Isn't it "open = not contact" instead?
        return model.devices.WindowState(device=self, value=self.open)

    def process_telegram(self, telegram, server):
        window_state = self.parse_readings(telegram)
        window_state.save()


class LightMovementSensor(model.devices.LightMovementSensor):

    def parse_readings(self, data_bytes):
        voltage = data_bytes[0] * 5.12 / 255.0
        brightness = data_bytes[1] * 512 / 255.0
        movement = ((data_bytes[3] & 0x02) >> 1) == 0

        r_volt = model.devices.Voltage(device=self, value=voltage).save()
        r_bright = model.devices.Brightness(device=self, value=brightness).save()
        r_mov = model.devices.Movement(device=self, value=movement).save()

        logger.info("EnOcean light/movement: Voltage = {}V, brightness = {}, movement = {}.".format(voltage, brightness, movement))

        return r_volt, r_bright, r_mov

    def process_telegram(self, telegram, server):
        voltage, brightness, movement = self.parse_readings(self, telegram.data_bytes)

        voltage.save()
        brightness.save()
        movement.save()


# Actuators
class Lamp(model.devices.Actuator, model.devices.Lamp):

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContact(device_id=telegram.sensor_id)

    if telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)

    if telegram.device_type == Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)

    return None
