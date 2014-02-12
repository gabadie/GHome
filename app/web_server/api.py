#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

from collections import defaultdict
from datetime import datetime
from collections import defaultdict, Counter
import calendar
import json
import xmlrpclib
import math

from geopy import geocoders
from metwit import Metwit
from flask import request, jsonify, Blueprint, current_app
import mongoengine

from enocean.devices import Sensor, Actuator, Lamp
from model.event import Connection
from model.devices import NumericReading
from model.fashion import Product
from model.house import Room
from model.meteo import Location
from model.meteo import Weather

from config import GlobalConfig
config = GlobalConfig()

# \ ! / Monkey patching mongoengine to make json dumping easier
mongoengine.Document.to_dict = lambda s : json.loads(s.to_json())

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
    connections = list()
    for e_name, e in sensor.events.iteritems():
        e_connections = [dump_connection(c) for c in Connection.objects(triggering_event=e)]

        for c in e_connections:
            c['triggering_event'] = e_name

        connections.extend(e_connections)

    s_json['connections'] = connections

    last_readings = dict()
    for reading_name, reading in sensor.last_readings.iteritems():
        last_readings[reading_name] = json.loads(reading.to_json())

    s_json['last_readings'] = last_readings

    return s_json

def dump_connection(connection):
    c_json = json.loads(connection.to_json())
    c_json['receiving_object'] = json.loads(connection.receiving_object.to_json())
    c_json['triggering_event'] = json.loads(connection.triggering_event.to_json())
    return c_json

## API

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


@rest_api.route('/connection/graph')
def connections_graph():
    result = dict(nodes=[], edges=[])

    actuators = Actuator.objects
    sensors = Sensor.objects

    n = len(actuators) + len(sensors)
    i = 0
    # Adding actuators
    for actuator in actuators:
        i += 1
        actuator_repr = dict(id=str(actuator.device_id),
                           label='{}'.format(actuator.name),
                           x=math.cos(2 * i * math.pi / n),
                           y=math.sin(2 * i * math.pi / n),
                           color='#395FBD',
                           size=6)

        result['nodes'].append(actuator_repr)

    edges_count = Counter()

    # Adding sensors and edges
    for sensor in sensors:
        i += 1
        sensor_repr = dict(id=str(sensor.device_id),
                           label='{}'.format(sensor.name),
                           x=math.cos(2 * i * math.pi / n),
                           y=math.sin(2 * i * math.pi / n),
                           color='#ec5148',
                           size=4)

        result['nodes'].append(sensor_repr)

        for e_name, event in sensor.events.iteritems():
            connections = Connection.objects(triggering_event=event)
            for c in connections:
                edges_count[(sensor.device_id, c.receiving_object.device_id)] += 1

    # Adding edges
    for sensor_id, actuator_id in edges_count:
        e_repr = dict(id='{}-{}'.format(str(sensor_id), str(actuator_id)),
                      source=str(sensor_id),
                      target=str(actuator_id))
        result['edges'].append(e_repr)



    return json.dumps(result, indent=4)

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
    result = dict()
    for Reading in NumericReading.__subclasses__():
        readings_map = defaultdict(list)
        for reading in Reading.objects:
            device = reading.device

            label = '{} - {}'.format(device.device_id, device.name)
            timestamp = calendar.timegm(reading.date.utctimetuple()) * 1000
            data = [timestamp, reading.value]

            readings_map[(label, device.device_id)].append(data)

        result[Reading.__name__] = [dict(key=label, values=v, id=device_id)
                                    for (label, device_id), v in readings_map.iteritems()]

    return json.dumps(result)


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

@rest_api.route('/sensor/position', methods=['POST'])
def set_sensor_position():
    sensor_id = request.json['sensor_id']
    x, y = request.json['x'], request.json['y']
    sensor = Sensor.objects.get(device_id=sensor_id)
    sensor.x, sensor.y = x, y
    sensor.save()

    return json.dumps(dict(ok=True, sensor=dump_sensor(sensor)))

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

## API
@rest_api.route('/player', methods=['POST','GET'])
def playMusic():
    if request.method == 'POST':
        form = request.form
        tags =  [form.get(val) for val in ['tag']]
        print tags
        urls_name, urls_img = rpc.raspi.find_music_url(0,tags)
    return jsonify(name=urls_name,  tags=tags, img=urls_img)

@rest_api.route('/player/tags', methods=['POST','GET'])
def playMusicViaTag():
    if request.method == 'POST':
        tags = [json.loads(request.data)]
        urls_name, urls_img = rpc.raspi.find_music_url(0,tags)
    return jsonify(name=urls_name,  tags=tags, img=urls_img)


@rest_api.route('/player/pause', methods=['POST','GET'])
def pauseMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.pause_music(0)
        if b_result == True :
            return jsonify( src="../static/img/player_play.png")
        return jsonify( src="../static/img/player_pause.png")

@rest_api.route('/player/next', methods=['POST','GET'])
def nextMusic():
    if request.method == 'POST':
        result = rpc.raspi.next_music(0)
        return jsonify( name = result )

@rest_api.route('/player/previous', methods=['POST','GET'])
def previousMusic():
    if request.method == 'POST':
        result = rpc.raspi.previous_music(0)
        return jsonify( name = result )


@rest_api.route('/product/search')
def products_search():
    # TODO : implement this
    products = json.loads(Product.objects.to_json())
    result = dict(ok=True, result=products)
    return json.dumps(result)

@rest_api.route('/meteo/setloc', methods=['POST','GET'])
def set_location():
    location = request.form.get('location')
    
    try:
        g = geocoders.GoogleV3()
        loc = g.geocode(location)

        if loc:
            name, (lat, lon) = loc
            [location.delete() for location in Location.objects]
            Location(name=name, latitude=lat, longitude=lon).save()
            result = dict(ok=True)
    except Exception as e:
        print e
        result = dict(ok=False)

    return json.dumps(result)

@rest_api.route('/meteo/weather', methods=['POST','GET'])
def get_weather():
    if len(Location.objects) > 0:
        location = Location.objects[0]
        try:
            content = Metwit.weather.get(location_lat=location.latitude, location_lng=location.longitude)

            dt = datetime.strptime(content[0]['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%S");
            content[0]['timestamp'] = dt.strftime("%A %d %B#%H:%M").capitalize()

            for i in range(1, len(content)):
                dt = datetime.strptime(content[i]['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%S");
                content[i]['timestamp'] = dt.strftime("%A %d %b#%H:%M").capitalize()
            result = dict(ok=True, geo=True, meteo=True, location=location.name, latitude=location.latitude, longitude=location.longitude, weather=content)
        except Exception as e:
            print e
            result = dict(ok=False, geo=True, meteo=False, location=location.name, latitude=location.latitude, longitude=location.longitude)
    else:
        result = dict(ok=False, geo=False, meteo=False)

    return json.dumps(result)

# House / Rooms
@rest_api.route('/room', methods=['GET'])
def get_rooms():
    rooms = [room.to_dict() for room in Room.objects]
    return json.dumps(dict(ok=True, result=rooms))