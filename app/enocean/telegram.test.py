#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telegram

if __name__ == '__main__':
    # A 'random' telegram, created only to test parsing and such
    t = telegram.Telegram([0xA5, 0x5A], h_seq=3, length=12, org=5, data=0x10080287,
                 sensor_id=39, status=2, checksum=136)
    assert t == telegram.from_bytes(t.bytes)
    assert t == telegram.from_str(str(t))
    assert t.sensor_id == 39

    # TODO : use "real" telegrams for testing

    # Listing_devices.pdf, page 12
    t = telegram.from_bytes([0xA5, 0x66, 0x0B, 0x07,
                    0x00, 0x84, 0x99, 0x0F,
                    0x00, 0x04, 0xE9, 0x57, 0x00, 0x01], strict=False)

    assert not t.valid_sync()

    # Example from Listing_devices.pdf
    t = telegram.from_bytes([0xA5, 0x5A, 0x0B, 0X07,
                    0X10, 0x08, 0x02, 0x87,
                    0x00, 0x04, 0xE9, 0x57, 0x00, 0x88], strict=False)

    assert t.valid_sync()
    assert t.mode == telegram.Telegram.TEACH_IN
    assert t.func == 4
    assert t.type == 1
    assert t.manufacturer_id == 0
    assert t.eep == (7, 4, 1)

    print "Tests passed !"