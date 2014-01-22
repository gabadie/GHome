#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

class GlobalConfig:

    class EnOcean:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.port = 8000

    class MainServer:
        def __init__(self):
            self.ip = "127.0.0.1"
            self.rpc_port = 8001

    def __init__(self):
        """ Construct with the development configuration """

        self.mongo_db = "ghome_development"
        self.api_8tracks =  "cd7a9189d060c79845828dc26471dbd6397cdb31"

        self.enocean = GlobalConfig.EnOcean()
        self.main_server = GlobalConfig.MainServer()

    def save_json(self, path):
        with open(path, 'w') as outfile:
            json_data = {
                'mongo_db': self.mongo_db,
                'enocean': {
                    'ip': self.enocean.ip,
                    'port': self.enocean.port
                },
                'main_server': {
                    'ip': self.main_server.ip,
                    'rpc_port': self.main_server.rpc_port
                }
            }

            json.dump(json_data, outfile)

            return True

        return False

    @staticmethod
    def from_json(path):
        config = GlobalConfig()

        with open(path) as file:
            json_content = json.load(file)

            config.mongo_db = json_content["mongo_db"]

            config.enocean.ip = json_content["enocean"]["ip"]
            config.enocean.port = int(json_content["enocean"]["port"])

            config.main_server.ip = json_content["main_server"]["ip"]
            config.main_server.rpc_port = int(json_content["main_server"]["rpc_port"])

            return config

        return None
