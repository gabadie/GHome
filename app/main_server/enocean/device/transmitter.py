#!/usr/bin/env python
# -*- coding: utf-8 -*-

from device import Device
from enocean.reading.thermometer import ThermometerReading

class TransmitterDevice(Device):
    def __init__(self, main_server, id):
        self.telegrams = []
        super(Device, self).__init__(main_server, id)
        
    def add_telegram(self, telegram):
        raise NotImplemented()
    
    def save(self):
        #TODO: database write access
        raise NotImplemented()
    