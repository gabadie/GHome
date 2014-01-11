#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from main_server.logger import Logger
from reading import ThermometerReading

class Device(object):

    # TODO : study every teach-in telegram in order to identify telegrams from their EEP
    @staticmethod
    def from_telegram(telegram):
        device = Thermometer(telegram.sensor_id)
        device.save()
        return device

    def __init__(self, device_id):
        self.id = device_id
        self.ignored = True


class Sensor(Device):
    def __init__(self, device_id):
        super(Sensor, self).__init__(device_id)

    def add_telegram(self, telegram, server):
        raise NotImplemented


class Thermometer(Sensor):
    def __init__(self, id):
        super(Thermometer, self).__init__(id)

    def add_telegram(self, telegram, server):
        reading = ThermometerReading(telegram.data_bytes)
        Logger.info("Thermometer reading from <{}>: {}°C, {}% humidity".format(telegram.sensor_id, reading.temperature,
        	                                                                   reading.humidity))