#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
sys.path.insert(0, '..')

from flask import Flask, render_template, request
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor
import mongoengine
from bson import json_util
import xmlrpclib

from model import core
from enocean.devices import Thermometer

from config import GlobalConfig
config = GlobalConfig()

# Initializing the app
app = Flask(__name__)
app.debug = True
rpc = xmlrpclib.Server('http://{}:{}/'.format(config.MainServer.ip, config.MainServer.rpc_port))
db = mongoengine.connect(config.mongo_db)

# TODO : remove this, for testing only
db.drop_database(config.mongo_db)
Thermometer(device_id='1337', name='Living room thermometer', ignored=False).save()
Thermometer(device_id='4242', name='Bedroom thermometer', ignored=True).save()
Thermometer(device_id='89351', name='Another thermometer', ignored=False).save()
Thermometer(device_id='34210', name='And yet another thermometer', ignored=False).save()

@app.route('/')
def index():
    devices = core.Device.objects()
    return render_template('index.html', devices=devices)

@app.route('/sensor', methods=['POST', 'GET'])
def add_sensor():
    if request.method == 'GET':
        resp = dict()
        return json_util.dumps(core.Device.objects())
    else:
        form = request.form
        sensor_id, sensor_name, sensor_type = form.get('id'), form.get('name'), form.get('type')

        print sensor_id, sensor_name, sensor_type

        return json.dumps(dict(status="ok"))


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

    # resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    # site = Site(resource)

    # reactor.listenTCP(5000, site)
    # reactor.run()