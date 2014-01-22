#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

import telegram
import model.devices
import logger


class Sensor(model.devices.Sensor):

    ignored = mongoengine.BooleanField(default=True)

    def process_telegram(self, telegram, server):
        raise NotImplementedError


# Sensors
class Thermometer(Sensor):

    @staticmethod
    def generate_telegram(sensor_id, temperature, humidity):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[1] = int(humidity * 250 / 100)
        data_bytes[2] = int(temperature * 250 / 40)
        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes):
        temperature = data_bytes[2] * 40 / 250.0
        humidity = data_bytes[1] * 100 / 250.0
        temp_r = model.devices.Temperature(device=self, value=temperature)
        humidity_r = model.devices.Humidity(device=self, value=humidity)

        logger.info("EnOcean thermometer #{}'s reading: Temperature = {}°C, Humidity = {}%".format(hex(self.device_id), temperature, humidity))

        return temp_r, humidity_r

    def process_telegram(self, telegram, server):
        temperature, humidity = self.parse_readings(telegram.data_bytes)

        temperature.save()
        humidity.save()

class Switch(Sensor):
    UNKNOWN, TOP, BOTTOM, RIGHT, LEFT = range(5)

    top_right = mongoengine.BooleanField(default=False)
    bottom_right = mongoengine.BooleanField(default=False)
    top_left = mongoengine.BooleanField(default=False)
    bottom_left = mongoengine.BooleanField(default=False)

    @staticmethod
    def generate_telegram(sensor_id, side, direction, pressed):
        data_bytes = [0x0 for i in xrange(4)]

        if not pressed:
            side = Switch.UNKNOWN
            direction = Switch.UNKNOWN
        else:
            data_bytes[0] = data_bytes[0] | 0x01

        if side == Switch.RIGHT:
            data_bytes[0] = data_bytes[0] | 0x04

        if direction == Switch.TOP:
            data_bytes[0] = data_bytes[0] | 0x02

        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes):
        print "Data bytes = {}".format(data_bytes)
        if data_bytes[0] & 0x10 == 0:
            side = Switch.UNKNOWN
            direction = Switch.UNKNOWN
            pressed = False
            self.top_right = False
            self.top_left = False
            self.bottom_right = False
            self.bottom_left = False
        else:
            side = Switch.RIGHT if (data_bytes[0] & 0x40) == 0x40 else Switch.LEFT

            if (data_bytes[0] & 0x20) == 0x20:
                direction = Switch.TOP
                if side == Switch.RIGHT:
                    self.top_right = not self.top_right
                else:
                    self.top_left = not self.top_left
            else:
                direction = Switch.BOTTOM
                if side == Switch.RIGHT:
                    self.bottom_right = not self.bottom_right
                else:
                    self.bottom_left = not self.bottom_left

            pressed = True
            
        logger.info("EnOcean switch #{}'s state has changed: top_right = {}, bottom_right = {}, top_left = {}, bottom_left = {}".format(
                                            hex(self.device_id), self.top_right, self.bottom_right, self.top_left, self.bottom_left))

        return model.devices.SwitchState(device=self, side=side, direction=direction, pressed=pressed)

    def process_telegram(self, telegram, server):
        switch_state = self.parse_readings(telegram.data_bytes)
        switch_state.save()


class WindowContact(Sensor):
    open = mongoengine.BooleanField(default=True)

    @staticmethod
    def generate_telegram(sensor_id, open):
        data_bytes = [0x0 for i in xrange(4)]
        if not open:
            data_bytes[3] = 0x01
        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes):
        self.open = ((data_bytes[3] & 0x01) == 0)
        logger.info("EnOcean window contactor #{}'s reading: open = {}".format(hex(self.device_id), self.open))

        return model.devices.WindowState(device=self, value=self.open)

    def process_telegram(self, telegram, server):
        window_state = self.parse_readings(telegram.data_bytes)
        window_state.save()


class LightMovementSensor(Sensor):

    @staticmethod
    def generate_telegram(sensor_id, voltage, brightness, movement):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[0] = int(voltage * 255 / 5.1)
        data_bytes[1] = int(brightness * 255 / 510)
        if not movement:
            data_bytes[3] = 0x01
        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes):
        voltage = data_bytes[0] * 5.1 / 255.0
        brightness = data_bytes[1] * 510 / 255.0
        movement = ((data_bytes[3] & 0x01) == 0x00)

        r_volt = model.devices.Voltage(device=self, value=voltage).save()
        r_bright = model.devices.Brightness(device=self, value=brightness).save()
        r_mov = model.devices.Movement(device=self, value=movement).save()

        logger.info("EnOcean light/movement sensor #{}'s reading: Voltage = {}V, brightness = {}, movement = {}.".format(hex(self.device_id), voltage, brightness, movement))

        return r_volt, r_bright, r_mov

    def process_telegram(self, telegram, server):
        voltage, brightness, movement = self.parse_readings(telegram.data_bytes)

        voltage.save()
        brightness.save()
        movement.save()


# Actuators
class Lamp(model.devices.Actuator):
    turned_on = mongoengine.BooleanField(required=True, default=False)

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(telegram):
    if telegram.device_type == telegram.Telegram.SRW01:
        return WindowContact(device_id=telegram.sensor_id)

    if telegram.device_type == telegram.Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)

    if telegram.device_type == telegram.Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)

    return None
