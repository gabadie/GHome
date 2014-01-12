#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# tcp : 80,443,4500
# udp : 4500
#

import sys

sys.path.insert(0, '..')

from server import MainServer
from config import GlobalConfig

configuration = GlobalConfig()
server = MainServer(configuration)
server.run()
