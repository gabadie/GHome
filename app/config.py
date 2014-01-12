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

    """ Construct with the development configuration """
    def __init__(self):
        self.mongo_db = "ghome_development"
        self.enocean = GlobalConfig.EnOcean()
        self.main_server = GlobalConfig.MainServer()

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

if __name__ == "__main__":

    config = GlobalConfig.from_json('insa_config.json')

    assert config.mongo_db == "ghome_database"
    assert config.enocean.ip == "134.214.106.23"
    assert config.enocean.port == 5000
    assert config.main_server.ip == "127.0.0.1"
    assert config.main_server.rpc_port == 8001

gateway_ip = "127.0.0.1"
gateway_port = 5000
db_name = "ghome_development"
api_8tracks =  "cd7a9189d060c79845828dc26471dbd6397cdb31"
