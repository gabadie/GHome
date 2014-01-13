#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tempfile
import config


def test_content(c):
    assert c.mongo_db == "ghome_database"
    assert c.enocean.ip == "134.214.106.23"
    assert c.enocean.port == 5000
    assert c.main_server.ip == "127.0.0.1"
    assert c.main_server.rpc_port == 8001

if __name__ == "__main__":
    c = config.GlobalConfig.from_json('insa_config.json')

    test_content(c)

    tmp_file = tempfile.mktemp(suffix=".json")
    c.save_json(tmp_file)
    c = config.GlobalConfig.from_json(tmp_file)

    test_content(c)

