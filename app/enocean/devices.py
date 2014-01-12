#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from twisted.internet import protocol

sys.path.insert(0, '..')

import model
import logger


class Thermometer(model.devices.Thermometer):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        return model.devices.Thermometer.Reading(device=thermometer, temperature=data_bytes[2] * 40 / 250.0, humidity=data_bytes[1] * 100 / 250.0)

    def proceed_telegram(self, telegram, server):
        reading = Thermometer.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean thermometer reading: temperature=" + str(reading.temperature) + "C, humidity=" + str(reading.humidity) + "%")


class WindowContact(model.devices.WindowContact):

    @staticmethod
    def reading_from_data_bytes(thermometer, data_bytes):
        contact = self.data_bytes[3] & 0x01
        if contact == 0:
            contact = True
        else:
            contact = False
        return model.devices.WindowContact.Reading(device=windowContact, open=contact)

    def proceed_telegram(self, telegram, server):
        reading = WindowContact.reading_from_data_bytes(self, telegram.data_bytes)
        reading.save()

        logger.info("EnOcean window contact reading: open=" + str(reading.open))


def from_telegram(self, telegram):
    if telegram.device_type == Telegram.SRW01:
        return WindowContact(device_id=telegram.sensor_id)
    elif telegram.device_type == Telegram.SR04RH:
        return Thermometer(device_id=telegram.sensor_id)
    
    raise NotImplemented
