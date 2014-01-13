#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
import logger


class Sensor(model.core.Sensor):
    ignored = mongoengine.BooleanField(default=True)

    def proceed_telegram(self, telegram, server):
        raise NotImplementedError

# Sensors
class Thermometer(Sensor, model.devices.Thermometer):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def proceed_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean thermometer reading: temperature=" + str(reading.temperature) + "C, humidity=" + str(reading.humidity) + "%")

class Switch(Sensor, model.devices.Switch):

    @staticmethod
    def reading_from_data_bytes(switch, data_bytes):
        return model.devices.Switch.Reading(turned_on=switch.on)

    def proceed_telegram(self, telegram, server):
        self.on = not self.on
        reading = Switch.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        self.activate()

        self.save()

        logger.info("EnOcean switch #{} activated".format(self.device_id))


class WindowContact(Sensor, model.devices.WindowContact):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        contact = (self.data_bytes[3] & 0x01) == 0
        self.open = contact

        # TODO : Isn't it "open = not contact" instead?
        return model.devices.WindowContact.Reading(device=windowContact, open=self.open)

    def proceed_telegram(self, telegram, server):
        reading = WindowContact.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean Window contact #{}: open={}".format(self.device_id, reading.open))


# Actuators
class Lamp(model.core.Actuator, model.devices.Lamp):

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(self, telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContact(device_id=telegram.sensor_id)
    elif telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    
    raise NotImplemented
