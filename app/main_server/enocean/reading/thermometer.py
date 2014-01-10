#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from reading import Reading

class ThermometerReading(Reading):
    def __init__(self, data_bytes):
        self.humidity = data_bytes[1] * 100 / 250.0
        self.temperature = data_bytes[2] * 40 / 250.0
        super(ThermometerReading, self).__init__()
    
    def save(self):
        #TODO: database write access
        raise NotImplemented()
        
        
if __name__ == "__main__":
    data_bytes = [0x00, 0x84, 0x99, 0x0F]
    reading = ThermometerReading(data_bytes)
    
    assert reading.humidity == 52.8
    assert reading.temperature == 24.48
    
    print "Tests passed !"
    