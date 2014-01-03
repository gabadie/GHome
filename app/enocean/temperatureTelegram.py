#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import Telegram

class TemperatureTelegram(Telegram):
    @staticmethod
    def from_bytes(bytes, strict=False):
        if len(bytes) != 14:
            raise InvalidTelegram("Invalid telegram length: {} (expected 14)".format(len(bytes)))

        sync_bytes = bytes[0:2]
        h_seq = (bytes[2] >> 5) & 0b111
        length = bytes[2] & 0b11111
        org = bytes[3]
        
        data = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[4:8]))
        data_bytes = [data >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]
        
        humidity = data_bytes[1] * 100 / 250.0
        
        temperature = data_bytes[2] * 40 / 250.0
        
        b7 = (data_bytes[3] & 0x80) >> 7
        b3 = (data_bytes[3] & 0x08) >> 3
        
        if b7 == 0 and b3 == 1:
            mode = Telegram.Mode.NORMAL
        elif b7 == 1 and b3 == 0:
            mode = Telegram.Mode.TEACH_IN
        else:
            mode = Telegram.Mode.UNKNOWN
        
        sensor_id = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[8:12]))
        status = bytes[12]
        checksum = bytes[13]
        
        return TemperatureTelegram(sync_bytes, h_seq, length, org, humidity, temperature, mode, sensor_id, status, checksum, strict)
	
    
    def __init__(self, sync_bytes, h_seq, length, org, humidity, temperature, mode, sensor_id, status, checksum, strict=False):
        self.humidity = humidity
        self.temperature = temperature
        
        data_humidity = hex(int(humidity * 250 / 100))
        data_temperature = hex(int(temperature * 250 / 40))
        if mode == Telegram.Mode.NORMAL:
            data_mode = '0x08'
        elif mode == Telegram.Mode.TEACH_IN:
            data_mode = '0x80'
        else:
            raise InvalidTelegram("Invalid mode: {}".format(mode))
        
        data_bytes = '0x00' + data_humidity[2:] + data_temperature[2:] + data_mode[2:]
        data = int(data_bytes, 16)
    
        super(TemperatureTelegram, self).__init__(sync_bytes, h_seq, length, org, data, sensor_id, status, checksum, strict)

	
    # Standard operators
    def __eq__(self, other):
        if not isinstance(other, TemperatureTelegram):
            return False
        else:
            return self.bytes == other.bytes


if __name__ == '__main__':
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