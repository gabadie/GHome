#!/usr/bin/env python
# -*- coding: utf-8 -*-

import enocean.telegram
import logger
import enocean.device.thermometer

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
        

class MainServer:

    def __init__(self):
        self.devices = {}
        self.authorized_devices = []
        
    def add_authorized_device(self, deviceId):
        authorized_devices.append(deviceId)

    def add_device(self, device):
        self.devices[device.id] = device
        
    def is_authorized(self, deviceId):
        return deviceId in self.authorized_devices
        
    def is_known(self, deviceId):
        return deviceId in self.devices
        
    def get_device(self, deviceId):
        return self.devices[deviceId];
        
    def telegram_received(self, telegram):
        Logger.info("Telegram received: " + telegram.bytes)
        
        if telegram.mode == Telegram.TEACH_IN:
            if not is_known(telegram.sensor_id):
                add_device(from_telegram(telegram))
                
        elif telegram.mode == Telegram.NORMAL and is_authorized(telegram.sensor_id):
            get_device(telegram.sensor_id).add_telegram(telegram)
            
        