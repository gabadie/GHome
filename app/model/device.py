#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from main_server.logger import Logger
from reading import ThermometerReading

class Device(object):
    @staticmethod
    def from_telegram(server, telegram):
        # TODO : study every teach-in telegram in order to identify telegrams from their EEP
        return Thermometer(server, telegram.sensor_id)
        Logger.error("Unknown device type")

    def __init__(self, main_server, id):
        self.main_server = main_server
        self.id = id
        self.ignored = True

    def save(self):
        self.main_server.devices[self.id] = id

class Sensor(Device):
    def __init__(self, main_server, id):
        super(Sensor, self).__init__(main_server, id)
        self.readings = []

    def add_reading(self, telegram):
        raise NotImplemented

    def save(self):
        #TODO: database write access
        raise NotImplemented


class Thermometer(Sensor):
    def __init__(self, main_server, id):
        super(Thermometer, self).__init__(main_server, id)

    def add_reading(self, telegram):
        reading = ThermometerReading(telegram.data_bytes)
        self.readings.append(reading)
        Logger.info("Thermometer reading from <{}>: {}°C, {}% humidity".format(telegram.sensor_id, reading.temperature,
        	                                                                   reading.humidity))

    def save(self):
        raise NotImplementedError
        #TODO: database write access