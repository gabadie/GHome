#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

from telegram import Telegram
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

        self.activated()
        self.save()

        logger.info("EnOcean switch #{} activated".format(self.device_id))


class WindowContact(Sensor, model.devices.WindowContact):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        contact = (self.data_bytes[3] & 0x01) == 0
        self.open = contact

        # TODO : Isn't it "open = not contact" instead?
        return model.devices.WindowContact.Reading(device=windowContact, open=self.open)


class LightMovementSensor(model.devices.LightMovementSensor):

    @staticmethod
    def reading_from_data_bytes(lightMovementSensor, data_bytes):
        movement = (self.data_bytes[3] & 0x02) >> 1
        if movement == 0:
            movement = True
        else:
            movement = False
        return model.devices.LightMovementSensor.Reading(device=lightMovementSensor, 
            voltage=data_bytes[0] * 5.12 / 255.0, brightness=data_bytes[1] * 512 / 255.0, movement=movement)

    def proceed_telegram(self, telegram, server):
        reading = LightMovementSensor.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()
        logger.info("EnOcean light and movement sensor reading: voltage=" + str(reading.voltage) + "V, brightness=" + str(reading.brightness) + "Lux, movement=" + str(reading.movement))


# Actuators
class Lamp(model.core.Actuator, model.devices.Lamp):

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        logger.info("Lamp #{} state changed. turned_on = {}".format(self.device_id, self.turned_on))

        self.save()


def from_telegram(telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContactor(device_id=telegram.sensor_id)
    
    if telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    
    if telegram.device_type == Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)
    
    return None