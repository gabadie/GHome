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
db = None


def init_db():
    """ For testing only """
    db.drop_database(config.mongo_db)

    # Actuators
    l1 = Lamp(device_id='889977', name='The main lamp', turned_on=True).save()
    l2 = Lamp(device_id='85654', name='Another lamp').save()

    # Sensors
    Thermometer(device_id='1337', name='Living room thermometer', ignored=False).save()
    Thermometer(device_id='4242', name='Bedroom thermometer', ignored=False).save()
    Thermometer(device_id='233232', name='A thermometer that should work', ignored=False).save()

    Switch(device_id='343830', name='A switch that should work', ignored=False, actuators=[l1, l2]).save()
    Switch(device_id='939400', name='An ignored switch', ignored=True).save()

    WindowContact(device_id='3311', name='A window contact sensor', open=False, ignored=True).save()

@app.route('/')
def index():
    actuators = core.Actuator.objects()
    sensor_types = Sensor.__subclasses__()

    lamps = Lamp.objects()

    return render_template('index.html', sensor_types=sensor_types, actuators=actuators, lamps=lamps)

@app.route('/sensor', methods=['POST', 'GET'])
def all_sensors():
    if request.method == 'GET':
        result = json.loads(Sensor.objects.to_json())
        resp = dict(ok=True, result=result)
    elif request.method == 'POST':
        form = request.form
        s_id, s_name, s_type, actuator_ids = [form.get(val, None) for val in ['id', 'name', 'type', 'actuators']]

        print "ACTUATORS ID = ", actuator_ids

        # Finding the actuators
        actuators = core.Actuator.objects(device_id__in=actuator_ids)
        if actuators is None:
            actuators = []

        print "ACTUATORS = ", actuators

        # Finding the sensor class
        SensorClass = [s_cls for s_cls in Sensor.__subclasses__() if s_cls.__name__ == s_type][0]

        # Creating the new device
        s = SensorClass(device_id=s_id, name=s_name, actuators=actuators, ignored=False)
        s.save()

        sensors = json.loads(Sensor.objects(device_id=s_id).to_json())
        if sensors:
            resp = dict(ok=True, result=sensors[0])
        else:
            resp = dict(ok=False)

    return json.dumps(resp)

@app.route('/sensor/<device_id>', methods=['GET', 'DELETE'])
def sensor(device_id):
    if request.method == 'GET':
        sensor = json.loads(Sensor.objects(device_id=device_id).to_json())[0]
        print sensor
        resp = dict(ok=True, result=sensor)
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

    if len(sys.argv) > 1:
        config = GlobalConfig.from_json(sys.argv[1])

    # init_db()
    db = mongoengine.connect(config.mongo_db)
    app.run(host="localhost", port=5000, debug=True)

    # resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    # site = Site(resource)

    # reactor.listenTCP(5000, site)
    # reactor.run()
