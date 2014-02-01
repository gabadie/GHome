#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import xmlrpclib
import calendar
import json
import sys
sys.path.insert(0, '..')

from flask import Flask, render_template, request, jsonify
import mongoengine

from model import devices
from enocean.devices import Sensor, Lamp

from config import GlobalConfig
config = GlobalConfig()

# Initializing the app
app = Flask(__name__)
app.debug = True
rpc = xmlrpclib.Server('http://{}:{}/'.format(config.main_server.ip, config.main_server.rpc_port))

def dump_sensor(sensor):
    s_json = json.loads(sensor.to_json())
    s_json['events'] = sensor.events.keys()
    s_json['type'] = sensor.__class__.__name__
    return s_json

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup')
def setup():
    actuators = devices.Actuator.objects()
    sensor_types = Sensor.__subclasses__()

    return render_template('setup.html', sensor_types=sensor_types, actuators=actuators)

@app.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')

@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/graph_data', methods=['GET'])
def graph_data():
    temp_map = defaultdict(list)
    for temperature in devices.Temperature.objects():
        device = temperature.device

        key = '{} - {}'.format(device.device_id, device.name)
        timestamp = calendar.timegm(temperature.date.utctimetuple()) * 1000
        data = [timestamp, temperature.value]

        temp_map[key].append(data)

    res = [dict(key=k, values=v) for k, v in temp_map.iteritems()]

    return json.dumps(res)


# Devices

@app.route('/sensor', methods=['POST', 'GET'])
def all_sensors():
    if request.method == 'GET':
        result = [dump_sensor(sensor) for sensor in Sensor.objects]
        resp = dict(ok=True, result=result)
    elif request.method == 'POST':
        form = request.form
        s_id, s_name, s_type = [form.get(val) for val in ['id', 'name', 'type']]

        print s_id, s_name, s_type

        # Converting from hexa representation
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

@app.route('/sensor/<device_id>', methods=['GET', 'DELETE'])
def sensor(device_id):
    device_id = int(device_id)
    if request.method == 'GET':
        sensor = json.loads(Sensor.objects(device_id=device_id).to_json())[0]
        print sensor
        resp = dict(ok=True, result=sensor)
    elif request.method == 'DELETE':
        device = Sensor.objects(device_id=device_id).first()
        print device
        if device:
            device.delete()
        resp = dict(ok=True, device_id=device_id)

    return json.dumps(resp)

@app.route('/sensor/<device_id>/ignored', methods=['POST', 'GET'])
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

@app.route('/lamp/', methods=['GET'])
def lamps():
    if request.method == 'GET':
        lamps = json.loads(Lamp.objects().to_json())
        resp = dict(ok=True, result=lamps)

    return json.dumps(resp)

# Music player

@app.route('/player', methods=['POST','GET'])
def playMusic():
    if request.method == 'POST':
        form = request.form
        tags =  [form.get(val) for val in ['tag']]
        print tags
        urls = rpc.raspi.find_music_url(0,tags)
        print "qdsf"
    return jsonify(name=urls)


@app.route('/player/pause', methods=['POST','GET'])
def pauseMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.pause_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")

@app.route('/player/next', methods=['POST','GET'])
def nextMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.next_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")

@app.route('/player/previous', methods=['POST','GET'])
def previousMusic():
    if request.method == 'POST':
        b_result = rpc.raspi.previous_music(0)
        if b_result == True :
            return jsonify( result="Play")
        return jsonify("Pausing", result="Pause")


@app.route('/music')
def music():
    user="Adrien"
    combo_options = ["jazzy", "happy", "sad", "worry"] #TODO this in the config file ?
    return render_template("music.html", combo_options=combo_options, user=user)


if __name__ == "__main__":

    if len(sys.argv) > 1:
        config = GlobalConfig.from_json(sys.argv[1])
    db = mongoengine.connect(config.mongo_db)

    app.run(host="localhost", port=config.web_server.port, debug=True)
