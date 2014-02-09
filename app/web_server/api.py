#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

from collections import defaultdict
import calendar
import json
import xmlrpclib

from geopy import geocoders 
from metwit import Metwit
from flask import request, jsonify, Blueprint, current_app

from enocean.devices import Sensor, Actuator, Lamp
from model.event import Connection
from model.devices import Temperature
from model.fashion import Product

from config import GlobalConfig
config = GlobalConfig()

rpc = xmlrpclib.Server('http://{}:{}/'.format(config.main_server.ip, config.main_server.rpc_port))


rest_api = Blueprint('rest_api', __name__)

## Utility functions
def dump_actuator(actuator):
    a_json = json.loads(actuator.to_json())
    a_json['callbacks'] = actuator.callbacks.keys()
    return a_json

def dump_sensor(sensor):
    s_json = json.loads(sensor.to_json())
    s_json['events'] = sensor.events.keys()
    s_json['type'] = sensor.__class__.__name__

    # TODO : find a way to render the sensors without putting this into each sensor's data
    s_json['actuators'] = [dump_actuator(actuator) for actuator in Actuator.objects]

    # TODO : Dirty hack to get events' name
    connections = dict()
    for e_name, e in sensor.events.iteritems():
        connections = [dump_connection(c) for c in Connection.objects(triggering_event=e)]
        for c in connections:
            c['triggering_event'] = e_name

    s_json['connections'] = connections

    return s_json

def dump_connection(connection):
    c_json = json.loads(connection.to_json())
    c_json['receiving_object'] = json.loads(connection.receiving_object.to_json())
    c_json['triggering_event'] = json.loads(connection.triggering_event.to_json())
    return c_json

## API
@rest_api.route('/player', methods=['POST','GET'])
def playMusic():
    if request.method == 'POST':
        form = request.form
        tags =  [form.get(val) for val in ['tag']]
        print tags
        urls = rpc.raspi.find_music_url(0,tags)
        print "qdsf"
    return jsonify(name=urls)

@rest_api.route('/connection', methods=['GET', 'POST'])
def event_binding():

    if request.method == 'GET':
        connections = [dump_connection(c) for c in Connection.objects]
        resp = dict(ok=True, result=connections)
        return json.dumps(resp)

    elif request.method == 'POST':
        sensor_id, s_event = request.json['sensor'], request.json['event']
        actuator_id, callback = request.json['actuator'], request.json['callback']

        sensor = Sensor.objects.get(device_id=sensor_id)
        actuator = Actuator.objects.get(device_id=actuator_id)

        current_app.logger.info(sensor.events[s_event])
        current_app.logger.info(actuator.callbacks[callback])

        try:
            connection = sensor.events[s_event].connect(actuator.callbacks[callback])
        except ValueError as e:
            resp = dict(ok=False, result=str(e))
            return json.dumps(resp)

        connection_json = dump_connection(connection)
        connection_json['triggering_event'] = s_event

        resp = dict(ok=True, result=connection_json)
        return json.dumps(resp)


@rest_api.route('/connection/<connection_id>', methods=['GET', 'DELETE'])
def event_connection(connection_id):
    resp = dict(ok=False)
    connection = Connection.objects.get(id=connection_id)

    if connection is None:
        return json.dumps(resp)
    elif request.method == 'GET':
        c_json = dump_connection(connection)
        resp = dict(ok=True, result=c_json)
    elif request.method == 'DELETE':
        connection.delete()
        resp = dict(ok=True)

    return json.dumps(resp)

@rest_api.route('/sensor/<sensor_id>/connections', methods=['GET'])
def sensor_connections(sensor_id):
    resp = dict(ok=False)
    if request.method == 'GET':
        sensor = Sensor.objects.get(device_id=sensor_id)
        resp = dict(ok=True, result=dump_sensor(sensor)['connections'])

    return json.dumps(resp)

# Monitoring
@rest_api.route('/graph_data', methods=['GET'])
def graph_data():
    temp_map = defaultdict(list)
    for temperature in Temperature.objects():
        device = temperature.device

        key = '{} - {}'.format(device.device_id, device.name)
        timestamp = calendar.timegm(temperature.date.utctimetuple()) * 1000
        data = [timestamp, temperature.value]

        temp_map[key].append(data)

    res = [dict(key=k, values=v) for k, v in temp_map.iteritems()]

    return json.dumps(res)


# Devices
@rest_api.route('/sensor', methods=['POST', 'GET'])
def all_sensors():
    if request.method == 'GET':
        result = [dump_sensor(sensor) for sensor in Sensor.objects]
        resp = dict(ok=True, result=result)
    elif request.method == 'POST':
        form = request.form
        s_id, s_name, s_type = [form.get(val) for val in ['id', 'name', 'type']]

        current_app.logger.info((s_id, s_name, s_type))

        # Converting from hexadecimal representation
        s_id = int(s_id, 16)

        # Finding the sensor class
        SensorClass = [s_cls for s_cls in Sensor.__subclasses__() if s_cls.__name__ == s_type][0]

        # Creating the new device
        s = SensorClass(device_id=s_id, name=s_name, ignored=False)
        s.save()

        sensors = json.loads(Sensor.objects(device_id=s_id).to_json())
        if sensors:
            resp = dict(ok=True, result=sensors[0])
        else:
            resp = dict(ok=False)

    return json.dumps(resp)

@rest_api.route('/sensor/<device_id>', methods=['GET', 'DELETE'])
def sensor(device_id):
    device_id = int(device_id)
    if request.method == 'GET':
        s = Sensor.objects.get(device_id=device_id)
        if s is None:
            resp = dict(ok=True, result="Couldn't find sensor")
        else:
            sensor = json.loads(s.to_json())
            resp = dict(ok=True, result=sensor)
    elif request.method == 'DELETE':
        device = Sensor.objects(device_id=device_id).first()
        print device
        if device:
            device.delete()
        resp = dict(ok=True, device_id=device_id)

    return json.dumps(resp)

@rest_api.route('/sensor/<device_id>/ignored', methods=['POST', 'GET'])
def sensor_ignored(device_id):
    device_id = int(device_id)

    if request.method == 'GET':
        ignored = Sensor.first(device_id=device_id).ignored
        resp = dict(ok=True, result=ignored)
    elif request.method == 'POST':
        print Sensor.objects(device_id=device_id)
        print Sensor.objects(device_id=int(device_id))
        sensor = Sensor.objects(device_id=device_id).first()
        sensor.ignored = request.json['value']
        sensor.save()
        resp = dict(ok=True, result=dump_sensor(sensor))

    return json.dumps(resp)

@rest_api.route('/lamp/', methods=['GET'])
def lamps():
    if request.method == 'GET':
        lamps = json.loads(Lamp.objects().to_json())
        resp = dict(ok=True, result=lamps)

    return json.dumps(resp)

@rest_api.route('/player/pause', methods=['POST','GET'])
def pauseMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.pause_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")

@rest_api.route('/player/next', methods=['POST','GET'])
def nextMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.next_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")

@rest_api.route('/player/previous', methods=['POST','GET'])
def previousMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.previous_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")


@rest_api.route('/product/search')
def products_search():
    # TODO : implement this
    products = json.loads(Product.objects.to_json())
    result = dict(ok=True, result=products)
    return json.dumps(result)

@rest_api.route('/meteo/weather', methods=['POST','GET'])
def get_location():
    if request.method =='POST':
        location = request.form.get('location')
        
        g = geocoders.GoogleV3()
        loc = g.geocode(location)
        
        if loc is None:
            result = dict(ok=False, geo=False, meteo=False, location=None)
        else:
            place, (lat, lon) = loc
            content = Metwit.weather.get(location_lat=lat, location_lng=lon)
            result = dict(ok=True, geo=True, meteo=True, location=place, latitude=lat, longitude=lon, weather=content)
        
        return json.dumps(result)

