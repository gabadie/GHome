#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MainServer:

    def __init__(self):
        self.devices = {}

    def getDevice(self, deviceId):
        return self.devices[deviceId];

