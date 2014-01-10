#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

class InvalidTelegram(Exception):
    pass

class NotImplemented(Exception):
    pass

class Telegram(object):
    VALID_SYNC_BYTES = [0xA5, 0x5A]
    UNKNOWN, NORMAL, TEACH_IN = range(3)

    @staticmethod
    def from_str(string, strict=False):
        if len(string) != 28:
            raise InvalidTelegram("Invalid telegram string: {} characters (expected 28)".format(len(string)))

        bytes = bytearray.fromhex(string)
        return Telegram.from_bytes(bytes, strict)

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

        if strict and not self.valid_mode():
            raise InvalidTelegram("Invalid mode byte: {}".format(self.data_bytes[3]))

    def valid_sync(self):
        return self.sync_bytes == Telegram.VALID_SYNC_BYTES

    def valid_checksum(self):
        return self.checksum == self.actual_checksum

    def valid_mode(self):
        return self.mode != Telegram.Mode.UNKNOWN

    def valid(self):
        return self.valid_sync() and self.valid_checksum() and self.valid_mode()

    # Properties
    @property
    def bytes(self):
        """
            Structure of an EnOcean telegram:

            BYTES 0-1: Sync Byte 1 (should be [0xA5, 0x5A])
            BYTE 2: H_SEQ (3 bits, the telegram's function) + Length of the telegram (5 bits)
            BYTE 3: ORG (0x05 → RPS, 0x06 → 1BS, 0x07 → 4BS)
            BYTES 4-7: The telegram's data encoded on 4 bytes
            BYTES 8-11: The sensor's id encoded on 4 bytes
            BYTE 12: Status Byte
            BYTE 13: Checksum (lower byte of the sum of all bytes except sync bytes and the checksum itself)
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
        return sum(self.bytes[2:13]) & 0xFF

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
    def mode(self):
        b7 = (self.data_bytes[3] & 0x80) >> 7
        b3 = (self.data_bytes[3] & 0x08) >> 3

        if b7 == 0 and b3 == 1:
            return Telegram.NORMAL
        elif b7 == 1 and b3 == 0:
            return Telegram.TEACH_IN
        else:
            return Telegram.UNKNOWN

    def requires_teach_in(function):
        """ A decorator for function that require the teach in mode """
        def wrapped(self, *args, **kwargs):
            if self.mode != Telegram.TEACH_IN:
                raise NotImplemented("Accessing teach-in attributes for a telegram that isn't in this mode.")
            return function(self, *args, **kwargs)
        return wrapped

    @property
    @requires_teach_in
    def func(self):
        return self.data_bytes[0] >> 2

    @property
    @requires_teach_in
    def type(self):
        return (self.data_bytes[0] & 0b11) << 5 | self.data_bytes[1] >> 3

    @property
    @requires_teach_in
    def manufacturer_id(self):
        return (self.data_bytes[1] & 0b111) << 5 | self.data_bytes[2] >> 3

    @property
    @requires_teach_in
    def eep(self):
        return (self.org, self.func, self.type)

    # Standard operators
    def __str__(self):
        return ''.join('{:02x}'.format(b).upper() for b in self.bytes)

    def __eq__(self, other):
        if not isinstance(other, Telegram):
            return False
        else:
            return self.bytes == other.bytes

if __name__ == '__main__':
    # A 'random' telegram, created only to test parsing and such
    t = Telegram([0xA5, 0x5A], h_seq=3, length=12, org=5, data=0x10080287,
                 sensor_id=39, status=2, checksum=136)
    assert t == Telegram.from_bytes(t.bytes)
    assert t == Telegram.from_str(str(t))
    assert t.sensor_id == 39

    # TODO : use "real" telegrams for testing

    # Listing_devices.pdf, page 12
    t = Telegram.from_bytes([0xA5, 0x66, 0x0B, 0x07,
                             0x00, 0x84, 0x99, 0x0F,
                             0x00, 0x04, 0xE9, 0x57, 0x00, 0x01], strict=False)

    assert not t.valid_sync()

    # Example from Listing_devices.pdf
    t = Telegram.from_bytes([0xA5, 0x5A, 0x0B, 0X07,
                             0X10, 0x08, 0x02, 0x87,
                             0x00, 0x04, 0xE9, 0x57, 0x00, 0x88], strict=False)

    assert t.valid_sync()
    assert t.mode == Telegram.TEACH_IN
    assert t.func == 4
    assert t.type == 1
    assert t.manufacturer_id == 0
    assert t.eep == (7, 4, 1)

    print "Tests passed !"