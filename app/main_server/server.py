#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import os
import subprocess
import sys
from twisted.internet import reactor
import twisted.web
import tempfile
import time

sys.path.insert(0, '..')

import enocean.client
from rpc_server import RpcServer


class MainServer(object):

    def __init__(self, config):
        self.config = config
        self.db = mongoengine.connect(config.mongo_db)
        self.rpc_server = None

        logger.info('main server initialized')

    def run(self):
        logger.info('running main server...')

        """ EnOcean client protocol factory """
        reactor.connectTCP(self.config.enocean.ip, self.config.enocean.port, enocean.client.ClientProtocolFactory(self))

        """ Launchs XML RPC server """
        self.rpc_server = RpcServer(self)
        reactor.listenTCP(self.config.main_server.rpc_port, twisted.web.server.Site(self.rpc_server))

        """ Main loop """
        reactor.run()


class MainServerProcess(object):

    def __init__(self, config):
        self.config = config

        config_path = tempfile.mktemp(suffix=".json")
        config.save_json(config_path)

        self.process = subprocess.Popen(["python", __file__, config_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(__file__))

        time.sleep(0.1)

    def terminate(self):
        self.process.terminate()
        self.process.wait()
        return self.process.returncode

    @property
    def return_code(self):
        return self.process.returncode

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr


if __name__ == "__main__":
    import logger
    from config import GlobalConfig

    logger.add_file('log/main_server')

    configuration = GlobalConfig()

    if len(sys.argv) > 1:
        configuration = GlobalConfig.from_json(sys.argv[1])

    server = MainServer(configuration)
    server.run()
