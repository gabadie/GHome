#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import core
import readings

import sys
sys.path.insert(0, '..')

from main_server.logger import Logger

class Sensor(core.Device):
    def add_telegram(self, telegram, server):
        raise NotImplemented


class Thermometer(Sensor):
    def add_telegram(self, telegram, server):
        reading = readings.from_thermometer(self, telegram.data_bytes)
        reading.save()

        Logger.info("Thermometer reading from <{}>: {}°C, {}% humidity".format(telegram.sensor_id, reading.temperature, reading.humidity))
