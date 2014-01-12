#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config

if __name__ == "__main__":
    c = config.GlobalConfig.from_json('insa_config.json')

    assert c.mongo_db == "ghome_database"
    assert c.enocean.ip == "134.214.106.23"
    assert c.enocean.port == 5000
    assert c.main_server.ip == "127.0.0.1"
    assert c.main_server.rpc_port == 8001

