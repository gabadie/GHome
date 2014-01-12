#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
import logger


class Sensor(model.core.Device):
    ignored = mongoengine.BooleanField(default=True)


class Thermometer(Sensor, model.devices.Thermometer):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def proceed_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean thermometer reading: temperature=" + str(reading.temperature) + "C, humidity=" + str(reading.humidity) + "%")


class WindowContactor(Sensor, model.devices.WindowContactor):

    @staticmethod
    def reading_from_data_bytes(windowContactor, data_bytes):
        contact = self.data_bytes[3] & 0x01
        if contact == 0:
            contact = True
        else:
            contact = False
        return model.devices.WindowContactor.Reading(device=windowContactor, open=contact)

    def proceed_telegram(self, telegram, server):
        reading = WindowContactor.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean window contactor reading: open=" + str(reading.open))


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


def from_telegram(self, telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContactor(device_id=telegram.sensor_id)
    elif telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    elif telegram.device_type == Telegram.SR_MDS:
        return LightMovementSensor(device_id=telegram.sensor_id)
    
    raise NotImplemented
