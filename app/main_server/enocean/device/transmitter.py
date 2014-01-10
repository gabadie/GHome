#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from device import Device
from enocean.reading.thermometer import ThermometerReading

class TransmitterDevice(Device):
    def __init__(self, main_server, id):
        self.telegrams = []
        super(TransmitterDevice, self).__init__(main_server, id)
        
    def add_telegram(self, telegram):
        raise NotImplemented
    
    def save(self):
        #TODO: database write access
        raise NotImplemented
    