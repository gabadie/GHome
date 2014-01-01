#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Telegram(object):
    VALID_SYNC_BYTES = [0xA5, 0x5A]

    # TODO : Give default values for sync_bytes and checksum ?
    def __init__(self, sync_bytes, h_seq, length, org, data, packet_id, status, checksum):

    	self.sync_bytes = sync_bytes
    	self.h_seq = h_seq
    	self.length = length
    	self.org = org
    	self.data = data
    	self.packet_id = packet_id
    	self.status = status
        self.checksum = checksum

    @staticmethod
    def from_bytes(bytes):
        sync_bytes = bytes[0:2]
        h_seq = (bytes[2] >> 5) & 0b111
        length = bytes[2] & 0b11111
        org = bytes[3]
        data = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[4:8]))
        packet_id = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[8:12]))
        status = bytes[12]
        checksum = bytes[13]

        return Telegram(sync_bytes, h_seq, length, org, data, packet_id, status, checksum)

    def valid_sync(self):
        return self.sync_bytes == Telegram.VALID_SYNC_BYTES

    def valid_checksum(self):
        return self.checksum == sum(self.bytes()) & 0xFF

    def valid(self):
        return self.valid_sync() and self.valid_checksum()


    def bytes(self):
    	"""
    		Structure of an EnOcean telegram:

    		BYTE 0: Sync Byte 1 (should be 0xA5)
    		BYTE 1: Sync Byte 2 (should be 0x5A)
    		BYTE 2: H_SEQ (3 bits, the telegram's function) + Length of the telegram (5 bits)
    		BYTE 3: ORG (0x05 → RPS, 0x06 → 1BS, 0x07 → 4BS)
    		BYTES 4-7: The telegram's data encoded on 4 bytes
    		BYTES 8-11: The sensor's id encoded on 4 bytes
    		BYTE 12: Status Byte
    		BYTE 13: Checksum
    	"""

    	bytes = [0x0 for i in xrange(14)]

    	bytes[0:2] = self.sync_bytes

    	bytes[2] = (self.h_seq & 0b111) << 5 | (self.length & 0b11111)

    	bytes[3] = self.org & 0xFF
    	bytes[4:8] = [self.data >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]
    	bytes[8:12] = [self.packet_id >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]
        bytes[12] = self.status & 0xFF
        bytes[13] = self.checksum & 0xFF

        return bytes


if __name__ == '__main__':
    t = Telegram([0xA5, 0x5A], h_seq=3, length=12, org=5, data=0x11111111,
                 packet_id=39, status=2, checksum=36)
    
    print t.bytes() 
    print Telegram.from_bytes(t.bytes()).bytes()