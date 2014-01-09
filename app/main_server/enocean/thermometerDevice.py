#!/usr/bin/env python
# -*- coding: utf-8 -*-

from transmitterDevice import TransmitterDevice

class ThermometerDevice(TransmitterDevice):
    def __init__(self, main_server, id):
        super(TransmitterDevice, self).__init__(main_server, id)
    
    def save(self):
        #TODO: database write access