#!/usr/bin/env python
# -*- coding: utf-8 -*-

from server import Device
from reading.thermometer import ThermometerReading

class TransmitterDevice(Device):
    def __init__(self, main_server, id):
        self.telegrams = []
        super(Device, self).__init__(main_server, id)
        
    def add_telegram(self, telegram)
        raise NotImplemented()
        self.telegrams.append(ThermometerReading(telegram.data_bytes)
    
    def save(self):
        #TODO: database write access
    
    