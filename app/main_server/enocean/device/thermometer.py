#!/usr/bin/env python

import sys
sys.path.insert(0, '..')

from transmitter import TransmitterDevice

class ThermometerDevice(TransmitterDevice):
    def __init__(self, main_server, id):
        super(ThermometerDevice, self).__init__(main_server, id)
        
    def add_telegram(self, telegram):
        self.telegrams.append(ThermometerReading(telegram.data_bytes))
    
    def save(self):
        raise NotImplemented()
        #TODO: database write access
        