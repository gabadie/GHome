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
from enocean.devices import Sensor, Thermometer, Switch, Lamp, WindowContact

from config import GlobalConfig
config = GlobalConfig()

# Initializing the app
app = Flask(__name__)
app.debug = True
rpc = xmlrpclib.Server('http://{}:{}/'.format(config.main_server.ip, config.main_server.rpc_port))
db = mongoengine.connect(config.mongo_db)

# TODO : remove this, for testing only
db.drop_database(config.mongo_db)
Thermometer(device_id='1337', name='Living room thermometer', ignored=False).save()
Thermometer(device_id='4242', name='Bedroom thermometer', ignored=False).save()
Thermometer(device_id='34210', name='A thermometer we\'ll ignore', ignored=True).save()

Switch(device_id='13548', name='A random switch', ignored=False).save()
Switch(device_id='82596', name='An ignored switch', ignored=True).save()

WindowContact(device_id='3311', name='A window contact sensor', open=False, ignored=True).save()

Lamp(device_id='889977', name='The main lamp', ignored=False).save()



@app.route('/')
def index():
    sensors = Sensor.objects()
    actuators = core.Actuator.objects()
    sensor_types = Sensor.__subclasses__()

    return render_template('index.html', sensors=sensors, sensor_types=sensor_types, actuators=actuators)

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
