#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import tempfile
import subprocess
import time
import signal
import logger
from model import generator
from config import *


class AbstractServerProcess(object):
    # cwd: str
    # script_path: str
    # config: GlobalConfig

    def __init__(self, script_path, config=None, cwd=None, stdout=None, stderr=None):
        if isinstance(config, str):
            assert os.path.isfile(config)
            config = GlobalConfig.from_json(config)

        if not config:
            config = GlobalConfig()

        if not cwd:
            cwd = os.path.getcwd()

        assert os.path.isdir(cwd)
        assert os.path.isfile(os.path.join(cwd, script_path))

        self.cwd = cwd
        self.script_path = script_path
        self.config = config

        config_path = tempfile.mktemp(suffix=".json")
        config.save_json(config_path)

        self.process = subprocess.Popen(["python", script_path, config_path], stdout=stdout, stderr=stderr, cwd=cwd)

        time.sleep(0.5)

    def terminate(self):
        self.process.send_signal(signal.SIGKILL)
        self.process.terminate()
        self.process.wait()
        return self.process.returncode

    @property
    def pid(self):
        return self.process.pid

    @property
    def return_code(self):
        return self.process.returncode

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr

class MainServerProcess(AbstractServerProcess):

    def __init__(self, config, cwd="main_server/"):
        AbstractServerProcess.__init__(self,
            cwd=cwd,
            script_path="server.py",
            config=config
        )

class WebServerProcess(AbstractServerProcess):

    def __init__(self, config, cwd="web_server/"):
        AbstractServerProcess.__init__(self,
            cwd=cwd,
            script_path="webserver.py",
            config=config
        )

    def terminate(self):
        AbstractServerProcess.terminate(self)

        os.system("kill $(lsof -t -i:{})".format(self.config.web_server.port))

if __name__ == "__main__":
    config = None

    if len(sys.argv) > 1:
        config = GlobalConfig.from_json(sys.argv[1])
    else:
        config = GlobalConfig()

    model_generator = generator.Generator(config)
    model_generator.generate_sample()
    main_server = MainServerProcess(config)
    web_server = WebServerProcess(config)

    logger.info("main_server PID: {}".format(main_server.pid))
    logger.info("web_server PID: {}".format(web_server.pid))

    try:
        signal.pause()

    except KeyboardInterrupt:
        print
    except AttributeError:
        time.sleep(0.1)

    main_server.terminate()
    web_server.terminate()

