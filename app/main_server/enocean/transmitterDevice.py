#!/usr/bin/env python
# -*- coding: utf-8 -*-

from device import Device

class TransmitterDevice(Device):
    def __init__(self, main_server, id):
        super(Device, self).__init__(main_server, id)
    
    def save(self):
        #TODO: database write access
    
    