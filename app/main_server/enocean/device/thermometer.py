#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from sensor import SensorDevice
from logger import Logger
from enocean.reading.thermometer import ThermometerReading

class ThermometerDevice(SensorDevice):
    def __init__(self, main_server, id):
        super(ThermometerDevice, self).__init__(main_server, id)
        
    def add_reading(self, telegram):
        reading = ThermometerReading(telegram.data_bytes)
        self.readings.append(reading)
        Logger.info("Thermometer reading from <{}>: {}".format(telegram.sensor_id, reading.temperature)
                                            + u"\u00B0" + "C, {}% humidity".format(reading.humidity))
    
    def save(self):
        raise NotImplemented()
        #TODO: database write access
        