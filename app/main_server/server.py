#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enocean.telegram import Telegram
from logger import Logger
from enocean.device.thermometer import ThermometerDevice
from device import Device

class MainServer:

    def __init__(self):
        self.devices = {}
        Logger.init_logger()
        
    def set_device_ignored(self, deviceId, ignored):
        if self.is_known(deviceId):
            device = self.get_device(deviceId)
            device.ignored = ignored
            Logger.info("Device <{}>.ignored={}".format(deviceId, ignored))
        else:
            Logger.error("Unknown device <{}>".format(deviceId))

    def add_device(self, device):
        self.devices[device.id] = device
        Logger.info("{} {} added".format(device.__class__.__name__, device.id)) #Add sensor information
        
    def is_known(self, deviceId):
        return deviceId in self.devices
        
    def get_device(self, deviceId):
        return self.devices[deviceId];
        
    def telegram_received(self, telegram):
        Logger.info("Telegram received: " + telegram.__str__())
        
        if telegram.mode == Telegram.TEACH_IN and not self.is_known(telegram.sensor_id):
            self.add_device(Device.from_telegram(self, telegram))
                
        elif telegram.mode == Telegram.NORMAL and self.is_known(telegram.sensor_id):
            device = self.get_device(telegram.sensor_id)
            if not device.ignored:
                device.add_reading(telegram)
            
        else:
            Logger.warning("Unknown telegram mode")