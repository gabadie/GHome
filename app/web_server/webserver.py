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

Lamp(device_id='889977', name='The main lamp').save()
Lamp(device_id='85654', name='Another lamp').save()



@app.route('/')
def index():
    actuators = core.Actuator.objects()
    sensor_types = Sensor.__subclasses__()

    return render_template('index.html', sensor_types=sensor_types, actuators=actuators)

@app.route('/sensor', methods=['POST', 'GET'])
def all_sensors():
    if request.method == 'GET':
        result = json.loads(Sensor.objects.to_json())
        resp = dict(ok=True, result=result)
    elif request.method == 'POST':
        form = request.form
        s_id, s_name, s_type, actuators = [form.get(val) for val in ['id', 'name', 'type', 'actuators']]
        if actuators is None:
            actuators = []
        print s_id, s_name, s_type, actuators
        rpc.create_sensor(s_id, s_name, s_type, actuators)
        sensor = json.loads(Sensor.objects(device_id=s_id).to_json())[0]
        
        resp = dict(ok=True, result=sensor)

    return json.dumps(resp)

@app.route('/sensor/<device_id>', methods=['GET', 'DELETE'])
def sensor(device_id):
    if request.method == 'GET':
        sensor = Sensor.objects(device_id=device_id)
        resp = dict(ok=True, result=sensor.to_mongo())
    elif request.method == 'DELETE':
        sensor = Sensor.objects(device_id=device_id)
        sensor.delete()
        resp = dict(ok=True, device_id=device_id)

    return json.dumps(resp)

@app.route('/sensor/<device_id>/ignored', methods=['POST', 'GET'])
def sensor_ignored(device_id):
    if request.method == 'GET':
        ignored = Sensor.first(device_id=device_id).ignored
        resp = dict(ok=True, result=ignored)
    elif request.method == 'POST':
        rpc.ignore_sensor(device_id, request.json['ignored'])
        resp = dict(ok=True)

    return json.dumps(resp)


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

    # resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    # site = Site(resource)

    # reactor.listenTCP(5000, site)
    # reactor.run()
