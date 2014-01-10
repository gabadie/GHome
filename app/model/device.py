#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Device:

    def __init__(self, id, main_server):
        self.id = id
        self.main_server = main_server
        self.ignored = True

    def save(self):
        self.main_server.devices[self.id] = self

