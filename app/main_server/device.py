#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enocean.telegram import Telegram
import enocean.device.thermometer

class Device(object):

    @staticmethod
    def from_telegram(server, telegram):
        # TODO : study every teach-in telegram in order to identify telegrams
        # from their EEP
        return enocean.device.thermometer.ThermometerDevice(server, telegram.sensor_id)
        Logger.error("Unknown device type")

    def __init__(self, main_server, id):
        self.main_server = main_server
        self.id = id
        self.ignored = True

    def save(self):
        self.main_server.devices[self.id] = id
        