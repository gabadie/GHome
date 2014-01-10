#!/usr/bin/env python
# -*- coding: utf-8 -*-

from transmitter import TransmitterDevice

class ThermometerDevice(TransmitterDevice):
    def __init__(self, main_server, id):
        super(TransmitterDevice, self).__init__(main_server, id)
        
    def add_telegram(self, telegram):
        self.telegrams.append(ThermometerReading(telegram.data_bytes))
    
    def save(self):
        raise NotImplemented()
        #TODO: database write access
        