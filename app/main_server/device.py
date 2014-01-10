#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enocean.telegram

class Device:

    @staticmethod
    def from_telegram(server, telegram):
        # TODO : study every teach-in telegram in order to identify telegrams
        # from their EEP
        return ThermometerDevice(server, sensor_id)
        Logger.error("Unknown device type")

    def __init__(self, main_server, id):
        self.main_server = main_server
        self.id = id
        self.ignored = true
        Logger.init_logger()

    def save(self):
        self.main_server.devices[self.id] = id