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


class Lamp(model.core.Actuator):
    turned_on = mongoengine.BooleanField(default=False)

    def activate(self, sensor):
        self.turned_on = not self.turned_on
        self.save()


def from_telegram(self, telegram):
    #TODO: code all other devices
    return Thermometer(device_id=telegram.sensor_id)
