import json


class RpiGlobalConfig:

    class RpiServer(object):
        def __init__(self):
            self.ip="127.0.0.1"
            self.port=7080
            
    class MainServer(object):

        def __init__(self):
            self.ip="127.0.0.1"
            self.port=8001

    def __init__(self):
        self.mainServerRpi=RpiGlobalConfig.MainServer()
        self.rpiServer=RpiGlobalConfig.RpiServer()

    @staticmethod
    def from_json(pathConfig):

        config=RpiGlobalConfig()

        with  open(pathConfig) as fileConfig:
            jsonFile=json.load(fileConfig)
            config.mainServerRpi.ip=jsonFile["mainServerRpi"]["ip"]
            config.mainServerRpi.port=int(jsonFile["mainServerRpi"]["port"])

            config.rpiServer.ip=jsonFile["rpiServer"]["ip"]
            config.rpiServer.port=int(jsonFile["rpiServer"]["port"])

        return config

