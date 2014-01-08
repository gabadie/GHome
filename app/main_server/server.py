#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Device:

    def __init__(self, main_server, id):
        self.main_server = main_server
        self.id = id
        self.ignored = true

    def save(self):
        self.main_server.devices[self.id] = id

class MainServer:

    def __init__(self):
        self.devices = {}

    def getDevice(self, deviceId):
        return self.devices[deviceId];

