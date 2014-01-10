#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

from enocean.reading.reading import Reading

class ThermometerReading(Reading):
    def __init__(self, data_bytes):
        #TODO => thermometer device in constructor
        self.humidity = data_bytes[1] * 100 / 250.0
        self.temperature = data_bytes[2] * 40 / 250.0
        super(Reading, self).__init__()
    
    def save(self):
        #TODO: database write access
        raise NotImplemented()
    
"""
#DATA TO BYTES
    data_humidity = hex(int(humidity * 250 / 100))
    data_temperature = hex(int(temperature * 250 / 40))
    
    
    data_bytes = '0x00' + data_humidity[2:] + data_temperature[2:] + data_mode[2:]
    data = int(data_bytes, 16)

#TEST
	# Normal mode - A valid TemperatureTelegram value is A55A0B070084990F0004E9570001
    t = TemperatureTelegram([0xA5, 0x5A], h_seq=3, length=12, org=5, 
                humidity=52.8, temperature=24.48, mode=Telegram.Mode.NORMAL,
                sensor_id=39, status=2, checksum=1, strict=False)
                
    assert t.data_bytes[0] == 0
    assert t.data_bytes[1] == 132
    assert t.data_bytes[2] == 153
    assert t.humidity == 52.8
    assert t.temperature == 24.48
    assert t.mode == Telegram.Mode.NORMAL

    # Example from Listing_devices.pdf
    t = TemperatureTelegram.from_bytes([0xA5, 0x5A, 0x0B, 0x07, 0x00, 0x84, 0x99, 0x0F,
											0x00, 0x04, 0xE9, 0x57, 0x00, 0x01], strict=False)
    
    assert t.data_bytes[0] == 0
    assert t.data_bytes[1] == 132
    assert t.data_bytes[2] == 153
    assert t.humidity == 52.8
    assert t.temperature == 24.48
    assert t.mode == Telegram.Mode.NORMAL
    
    print 'Tests passed !'
"""