#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from device import Device
from enocean.reading.thermometer import ThermometerReading

class SensorDevice(Device):
    def __init__(self, main_server, id):
        self.readings = []
        super(SensorDevice, self).__init__(main_server, id)
        
    def add_reading(self, telegram):
        raise NotImplemented
    
    def save(self):
        #TODO: database write access
        raise NotImplemented
    