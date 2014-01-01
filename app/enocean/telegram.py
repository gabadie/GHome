#!/usr/bin/env python
# -*- coding: utf-8 -*-

class InvalidTelegram(Exception):
    pass


class Telegram(object):
    VALID_SYNC_BYTES = [0xA5, 0x5A]

    @staticmethod
    def from_bytes(bytes, strict=False):
        if len(bytes) != 14:
            raise InvalidTelegram("Invalid telegram length: {} (expected 14)".format(len(bytes)))

        sync_bytes = bytes[0:2]
        h_seq = (bytes[2] >> 5) & 0b111
        length = bytes[2] & 0b11111
        org = bytes[3]
        data = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[4:8]))
        sensor_id = sum(d << 8 * (3 - i) for i, d in enumerate(bytes[8:12]))
        status = bytes[12]
        checksum = bytes[13]

        return Telegram(sync_bytes, h_seq, length, org, data, sensor_id, status, checksum, strict)

    # TODO : Give default values for sync_bytes and checksum ?
    def __init__(self, sync_bytes, h_seq, length, org, data, sensor_id, status, checksum, strict=False):

        self.sync_bytes = sync_bytes
        self.h_seq = h_seq
        self.length = length
        self.org = org
        self.data = data
        self.sensor_id = sensor_id
        self.status = status
        self.checksum = checksum

        if strict and not self.valid_sync():
            raise InvalidTelegram("Invalid sync bytes: {}".format(sync_bytes))

        if strict and not self.valid_checksum():
            msg = "Invalid checksum. Expected: {}, Actual: {}".format(checksum, self.actual_checksum)
            raise InvalidTelegram(msg)

    def valid_sync(self):
        return self.sync_bytes == Telegram.VALID_SYNC_BYTES

    def valid_checksum(self):
        return self.checksum == self.actual_checksum

    def valid(self):
        return self.valid_sync() and self.valid_checksum()

    # Properties
    @property
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
        bytes[8:12] = [self.sensor_id >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]
        bytes[12] = self.status & 0xFF
        bytes[13] = self.checksum & 0xFF

        return bytes

    @property
    def actual_checksum(self):
        return sum(self.bytes[:13]) & 0xFF

    @property
    def rp_counter(self):
        return self.status & 0b1111

    @property
    def data_bytes(self):
        return [self.data >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]

    @property
    def id_bytes(self):
        return [self.sensor_id >> (8 * i) & 0xFF for i in [3, 2, 1, 0]]

    @property
    def func(self):
        return self.data_bytes[0] >> 2

    @property
    def type(self):
        return (self.data_bytes[0] & 0b11) << 5 | self.data_bytes[1] >> 3

    @property
    def manufacturer_id(self):
        return (self.data_bytes[1] & 0b111) << 5 | self.data_bytes[2] >> 3

    @property
    def epp(self):
        return (self.org, self.func, self.type)

    # Standard operators
    def __eq__(self, other):
        if not isinstance(other, Telegram):
            return False
        else:
            return self.bytes == other.bytes

if __name__ == '__main__':
    t = Telegram([0xA5, 0x5A], h_seq=3, length=12, org=5, data=0x11111111,
                 sensor_id=39, status=2, checksum=36)

    assert t == Telegram.from_bytes(t.bytes)

    # Example from Listing_devices.pdf
    t = Telegram.from_bytes([0xA5, 0x5A, 0x0B, 0X07, 0X10, 0x08, 0x02, 0x87,
                                                     0x00, 0x04, 0xE9, 0x57, 0x00, 0x88])

    assert t.valid_sync()
    assert t.func == 4
    assert t.type == 1
    assert t.manufacturer_id == 0
    assert t.epp == (7, 4, 1)

    print 'Tests passed !'