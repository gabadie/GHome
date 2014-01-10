#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enocean.telegram
from logger import Logger
from enocean.device.thermometer import ThermometerDevice

class MainServer:

    def __init__(self):
        self.devices = {}
        
    def add_authorized_device(self, deviceId):
        authorized_devices.append(deviceId)

    def add_device(self, device):
        self.devices[device.id] = device
        
    def is_known(self, deviceId):
        return deviceId in self.devices
        
    def get_device(self, deviceId):
        return self.devices[deviceId];
        
    def telegram_received(self, telegram):
        Logger.info("Telegram received: ".join(str(byte) for byte in telegram.bytes))
        
        if telegram.mode == Telegram.TEACH_IN and not is_known(telegram.sensor_id):
            add_device(from_telegram(telegram))
                
        elif telegram.mode == Telegram.NORMAL:
            device = get_device(telegram.sensor_id)
            if not device.ignore:
                device.add_telegram(telegram)
            