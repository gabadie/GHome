#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine

sys.path.insert(0, '..')

import logger
import telegram
import model.devices
from model import event
from model.trigger import Trigger

class Sensor(model.devices.Sensor):

    ignored = mongoengine.BooleanField(default=True)

    def process_telegram(self, telegram, server):
        raise NotImplementedError


# Sensors
class Thermometer(Sensor):
    temperature_triggers = mongoengine.ListField(mongoengine.ReferenceField(Trigger), default=list)
    humity_triggers      = mongoengine.ListField(mongoengine.ReferenceField(Trigger), default=list)
    _old_temperature = None
    _old_humidity    = None

    @staticmethod
    def generate_telegram(sensor_id, temperature, humidity):
        data_bytes = [0x0 for i in xrange(4)]
        data_bytes[1] = int(humidity * 250 / 100)
        data_bytes[2] = int(temperature * 250 / 40)
        data_bytes[3] = 0x01
        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes):
        if data_bytes[3] & 0x01 == 0:
            logger.info("EnOcean thermometer #{}'s is no longer available".format(hex(self.device_id)))
            return (False, 0, 0)

        temperature = data_bytes[2] * 40 / 250.0
        humidity = data_bytes[1] * 100 / 250.0
        temp_r = model.devices.Temperature(device=self, value=temperature)
        humidity_r = model.devices.Humidity(device=self, value=humidity)

        logger.info("EnOcean thermometer #{}'s reading: Temperature = {}°C, Humidity = {}%".format(hex(self.device_id), temperature, humidity))

        return (True, temp_r, humidity_r)

    def process_telegram(self, telegram, server):
        validity, temperature, humidity = self.parse_readings(telegram.data_bytes)

        if validity:
            temperature.save()
            humidity.save()

        # If there are cached values, trigger events
        if self._old_temperature != None and self._old_humidity != None:
            for t in self.temperature_triggers:
                t.trigger(self._old_temperature, temperature, server)

            for h in self.humidity_triggers:
                h.trigger(self._old_humidity, humidity, server)

        self._old_temperature = temperature
        self._old_humidity    = humidity


class Switch(Sensor):
    UNKNOWN, TOP, BOTTOM, RIGHT, LEFT = range(5)

    top_right = mongoengine.BooleanField(default=False)
    bottom_right = mongoengine.BooleanField(default=False)
    top_left = mongoengine.BooleanField(default=False)
    bottom_left = mongoengine.BooleanField(default=False)

    onclick_top_right = event.slot()
    onclick_bottom_right = event.slot()
    onclick_top_left = event.slot()
    onclick_bottom_left = event.slot()

    @staticmethod
    def generate_telegram(sensor_id, side, direction, pressed):
        data_bytes = [0x0 for i in xrange(4)]

        if not pressed:
            side = Switch.UNKNOWN
            direction = Switch.UNKNOWN
        else:
            data_bytes[0] = data_bytes[0] | 0x10

        if side == Switch.RIGHT:
            data_bytes[0] = data_bytes[0] | 0x40

        if direction == Switch.TOP:
            data_bytes[0] = data_bytes[0] | 0x20

        return telegram.sensor_telegram(sensor_id=sensor_id, data_bytes=data_bytes)

    def parse_readings(self, data_bytes, server):
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

                    if self.top_right:
                        self.onclick_top_right(server)

                else:
                    self.top_left = not self.top_left

                    if self.top_left:
                        self.onclick_top_left(server)

            else:
                direction = Switch.BOTTOM
                if side == Switch.RIGHT:
                    self.bottom_right = not self.bottom_right

                    if self.bottom_right:
                        self.onclick_bottom_right(server)
                else:
                    self.bottom_left = not self.bottom_left

                    if self.bottom_left:
                        self.onclick_bottom_left(server)

            pressed = True

        logger.info("EnOcean switch #{}'s state has changed: top_right = {}, bottom_right = {}, top_left = {}, bottom_left = {}".format(
                                            hex(self.device_id), self.top_right, self.bottom_right, self.top_left, self.bottom_left))

        return model.devices.SwitchState(device=self, side=side, direction=direction, pressed=pressed)

    def process_telegram(self, telegram, server):
        switch_state = self.parse_readings(telegram.data_bytes, server)
        switch_state.save()


class WindowContact(Sensor):
    open = mongoengine.BooleanField(default=True)

    opened  = event.slot()
    closed  = event.slot()

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

        if window_state == True:
            self.opened(server)
        else:
            self.closed(server)


class LightMovementSensor(Sensor):
    voltage_triggers    = mongoengine.ListField(mongoengine.ReferenceField(Trigger), default=list)
    brightness_triggers = mongoengine.ListField(mongoengine.ReferenceField(Trigger), default=list)
    moved = event.slot()

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
    turned_on = mongoengine.BooleanField(default=False)

    def turn_on(self, turned_on):
        self.turned_on = turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()

    def callback_turn_on(self, server):
        return self.turn_on(True)

    def callback_turn_off(self, server):
        return self.turn_on(False)

    def callback_toggle(self, server):
        return self.turn_on(not self.turned_on)

class Socket(model.devices.Actuator):
    activated = mongoengine.BooleanField(default=False)

    def activate(self, activated):
        self.activated = activated
        logger.info("Socket #{} state changed. activated = {}".format(self.device_id, self.activated))

        self.save()

    def callback_activate(self, server):
        if not self.activated:
            return self.callback_toggle()

    def  callback_deactivate(self, server):
        if self.activated:
            return self.callback_toggle()

    def callback_toggle(self, server):
        side = Switch.RIGHT
        if self.activated:
            direction = Switch.TOP
        else:
            direction = Switch.BOTTOM

        telegram = Switch.generate_telegram(sensor_id=self.device_id, side=side, direction=direction, pressed=True)
        server.enocean_protocol.send_data(str(telegram))

        return self.activate(not self.activated)


def from_telegram(telegram):
    if telegram.device_type == telegram.Telegram.SRW01:
        return WindowContact(device_id=telegram.sensor_id)

    if telegram.device_type == telegram.Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)

    if telegram.device_type == telegram.Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)

    return None
