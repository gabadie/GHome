#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# tcp : 80,443,4500
# udp : 4500
#

from server import MainServer

server = MainServer()
server.run()
