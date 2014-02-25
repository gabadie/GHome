#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import xmlrpclib

sys.path.insert(0, '..')

from global_server import MainServerProcess
import config

if __name__ == "__main__":
    c = config.GlobalConfig()
    server = MainServerProcess(c, cwd="./")

    rpc_client = xmlrpclib.Server('http://{}:{}/'.format(c.main_server.ip, c.main_server.rpc_port))
    assert rpc_client.ping("lala") == "lala"

    server.terminate()
