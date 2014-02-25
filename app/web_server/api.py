#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append('..')

from datetime import datetime
from datetime import timedelta
from collections import defaultdict, Counter
import calendar
import json
import xmlrpclib
import math

from geopy import geocoders
from metwit import metwit
from flask import request, jsonify, Blueprint, current_app
import mongoengine

from model.devices import Sensor, Actuator
from enocean.devices import Thermometer
from model.trigger import ThresholdTrigger
from model.event import Connection
from model.devices import NumericReading
from model.phone import Phone
from model.fashion import Product, OutfitChoice, fashion_product_rank
from model.house import Room
from model.meteo import Location
from model.meteo import Weather
import model.clock
import main_server.rpc_server
from model.devices import Device

from config import GlobalConfig
config = GlobalConfig()

# \ ! / Monkey patching mongoengine to make json dumping easier
mongoengine.Document.to_dict = lambda s : json.loads(s.to_json())

from config import GlobalConfig

rest_api = Blueprint('rest_api', __name__)
rpc = xmlrpclib.Server('http://{}:{}/'.format(GlobalConfig().main_server.ip, GlobalConfig().main_server.rpc_port))

## Utility functions
def dump_actuator(actuator):
    a_json = json.loads(actuator.to_json())
    a_json['callbacks'] = actuator.callbacks.keys()
    a_json['type'] = actuator.__class__.__name__
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

    if s_json['type'] == "Thermometer":
        s_json['is_thermometer'] = True
        s_json['temperature_triggers'] = [json.loads(trigger.to_json()) for trigger in sensor.temperature_triggers]

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
                           label='{}'.format(actuator.name.encode('utf-8')),
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

@rest_api.route('/trigger/<connection_id>', methods=['GET', 'POST'])
def trigger_connection(connection_id):
    resp = dict(ok=False)

    print request.method

    if request.method == 'GET':
        connection = Connection.objects.get(id=connection_id)
        c_json = dump_connection(connection)
        resp = dict(ok=True, result=c_json)
    elif request.method == 'POST':
        if rpc.trigger_connection(connection_id):
            resp = dict(ok=True)

    return json.dumps(resp)

@rest_api.route('/sensor/<sensor_id>/connections', methods=['GET'])
def sensor_connections(sensor_id):
    resp = dict(ok=False)
    if request.method == 'GET':
        sensor = Sensor.objects.get(device_id=sensor_id)
        resp = dict(ok=True, result=dump_sensor(sensor)['connections'])

    return json.dumps(resp)

# Monitoring (nvd3)
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

# xCharts data
@rest_api.route('/sensor/<device_id>/xcharts_data', methods=['GET'])
def xcharts_data(device_id):
    sensor = Sensor.objects.get(device_id=device_id)
    result = list()

    for Reading in NumericReading.__subclasses__():
        readings_map = dict(className='.{}'.format(Reading.__name__))
        readings_map['data'] = list()
        for reading in Reading.objects(device=sensor):

            label = datetime.strftime(reading.date, '%Y-%m-%dT%H:%M:%S')
            data = dict(x=label, y=reading.value)

            readings_map['data'].append(data)

        if readings_map['data']:
            result.append(readings_map)
    return jsonify(ok=True, result=result)

# Devices
@rest_api.route('/sensor', methods=['POST', 'GET'])
def all_sensors():
    if request.method == 'GET':
        result = [dump_sensor(sensor) for sensor in Sensor.objects]
        resp = dict(ok=True, result=result)
    elif request.method == 'POST':
        #Adding a device (sensor or actuator)
        form = request.form
        d_id, d_name, d_type, d_class = [form.get(val) for val in ['id', 'name', 'device-type', 'device-class']]

        current_app.logger.info((d_id, d_name, d_class))

        # Converting from hexadecimal representation
        d_id = int(d_id, 16)

        if Device.objects(device_id=d_id):
            print "already exist"
            resp = dict(ok=False)
            return json.dumps(resp)

        # Finding the sensor class
        subclasses = []
        for sub in Sensor.__subclasses__():
            subclasses.append(sub)

        for sub in Actuator.__subclasses__():
            subclasses.append(sub)

        DeviceClass = [d_cls for d_cls in subclasses if d_cls.__name__ == d_class][0]

        # Creating the new device
        d = DeviceClass(device_id=d_id, name=d_name, ignored=False)
        d.save()

        devices = json.loads(Device.objects(device_id=d_id).to_json())
        if devices:
            if d_type == "Sensor":
                resp = dict(ok=True, sensor=True, result=devices[0])
            else:
                resp = dict(ok=True, sensor=False, result=devices[0])
        else:
            resp = dict(ok=False)

    return json.dumps(resp)

@rest_api.route('/sensor/position', methods=['POST'])
def set_sensor_position():
    sensor_id = request.json['sensor_id']
    x, y, z = request.json['x'], request.json['y'], request.json['z']
    sensor = Sensor.objects.get(device_id=sensor_id)
    sensor.x, sensor.y, sensor.z = x, y, z
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

@rest_api.route('/actuator/', methods=['GET', 'POST'])
def actuators():
    actuators = [dump_actuator(actuator) for actuator in Actuator.objects]
    resp = dict(ok=True, result=actuators)

    return json.dumps(resp)

@rest_api.route('/phone/')
def phone():
    resp = dict(ok=True, result=json.loads(Phone.objects.to_json()))

    return json.dumps(resp)


@rest_api.route('/actuator/<device_id>', methods=['GET', 'DELETE'])
def actuator(device_id):
    device_id = int(device_id)
    if request.method == 'GET':
        a = Actuator.objects.get(device_id=device_id)
        if a is None:
            resp = dict(ok=True, result="Couldn't find actuator")
        else:
            actuator = json.loads(a.to_json())
            resp = dict(ok=True, result=actuator)
    elif request.method == 'DELETE':
        device = Actuator.objects(device_id=device_id).first()
        if device:
            device.delete()
            connections = Connection.objects(receiving_object=device)
            for c in connections:
                c.delete()
        resp = dict(ok=True, device_id=device_id)

    return json.dumps(resp)

## API
@rest_api.route('/player', methods=['POST','GET'])
def playMusic():
    if request.method == 'POST':
        form = request.form
        tags =  [form.get(val) for val in ['tag']]
        print tags
        result = json.loads(rpc.raspi.find_music_url(0,tags))
    return jsonify(name=result['result'], tags=tags, img="", ok=json.dumps(result['ok']))

def music_playing():
    music_playing = rpc.raspi.music_playing(0)
    return music_playing

@rest_api.route('/player/tags', methods=['POST','GET'])
def playMusicViaTag():
    if request.method == 'POST':
        tags = [json.loads(request.data)]
        result = json.loads(rpc.raspi.find_music_url(0,tags))
    return jsonify(name=result['result'], tags=tags, img="", ok=result['ok'])


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


@rest_api.route('/product/')
def products_search():
    fashion_product_rank

    def fashion_sort_by_rank(objects):
        l = [p.to_dict() for p in objects]
        l = sorted(l, key=lambda p: p['rank'], reverse=True)

        return l

    top = fashion_sort_by_rank(Product.objects(top=True))
    bottom = fashion_sort_by_rank(Product.objects(bottom=True))
    feet = fashion_sort_by_rank(Product.objects(feet=True))

    result = dict(ok=True, result=dict(top=top, bottom=bottom, feet=feet))
    return json.dumps(result)

# Threslhold
@rest_api.route('/outfit', methods=['POST'])
def new_outfit():
    outfit = OutfitChoice()

    outfit.top = Product.objects(id=request.json['top']).first()
    outfit.bottom = Product.objects(id=request.json['bottom']).first()
    outfit.feet = Product.objects(id=request.json['feet']).first()
    outfit.save()

    return json.dumps(dict(ok=True))

@rest_api.route('/meteo/getloc', methods=['POST','GET'])
def get_location():
    dt = datetime.now()
    time = dt.strftime("%A %d %b, %H:%M").capitalize()

    if len(Location.objects) > 0:
        location = Location.objects[0]
        name = location.name
        ok = True
        loc = True
    else:
        name = ''
        ok = False
        loc = False

    result = dict(ok=ok, loc=loc, location=name, time=time)

    return json.dumps(result)

@rest_api.route('/meteo/setloc', methods=['POST','GET'])
def set_location():
    location = request.form.get('location')

    try:
        g = geocoders.GoogleV3()
        loc = g.geocode(location)

        if loc:
            name, (lat, lon) = loc
            for location in Location.objects:
                location.delete()
            Location(name=name, latitude=lat, longitude=lon).save()
            if update_current_weather():
                result = dict(ok=True)
                return json.dumps(result)
    except Exception as e:
        print e

    result = dict(ok=False)

    return json.dumps(result)

def update_current_weather():
    if len(Location.objects) > 0:
        location = Location.objects[0]
        try:
            content = get_json_weather(lat=location.latitude, lon=location.longitude)

            [weather.delete() for weather in Weather.objects]

            td = timedelta(hours=location.hoursdelta)
            icon = content[0]['icon']
            humidity = content[0]['weather']['measured']['humidity']
            temperature = content[0]['weather']['measured']['temperature']

            Weather(expire=get_datetime(content[1]['timestamp']) + td, icon=icon, humidity=humidity, temperature=temperature).save()
            return True
        except Exception as e:
            print e
            return False


@rest_api.route('/meteo/currentweather', methods=['POST','GET'])
def get_curent_weather():
    if len(Location.objects) > 0:

        #Update current weather
        if len(Weather.objects) == 0 or Weather.objects[0].expire < datetime.now():
            if not update_current_weather():
                result = dict(ok=False, geo=True, meteo=False)
                return json.dumps(result)

        weather = Weather.objects[0]

        icon = weather.icon
        humidity = weather.humidity
        temperature = weather.temperature

        result = dict(ok=False, geo=True, meteo=True, icon=icon,
            humidity=humidity, temperature=temperature)

    else:
        result = dict(ok=False, geo=False, meteo=False)

    return json.dumps(result)

def get_json_weather(lat, lon):
    return Metwit.weather.get(location_lat=lat, location_lng=lon)

def get_datetime(utcstring):
    return datetime.strptime(utcstring.split('.')[0], "%Y-%m-%dT%H:%M:%S")

def get_timedelta(distantDateTime):
    return datetime.now().hour - distantDateTime.hour;

@rest_api.route('/meteo/weather', methods=['POST','GET'])
def get_weather():
    if len(Location.objects) > 0:
        location = Location.objects[0]
        try:
            content = get_json_weather(lat=location.latitude, lon=location.longitude)

            hoursdelta = get_timedelta(get_datetime(content[0]['timestamp']))
            location.hoursdelta = hoursdelta;
            location.save()
            print hoursdelta
            td = timedelta(hours=hoursdelta)

            for i in range(0, len(content)):
                dt = get_datetime(content[i]['timestamp']) + td;
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
# Threslhold
@rest_api.route('/threshold', methods=['POST'])
def new_threshold():
    thermometer_id = request.json['thermometer_id']
    threshold_name = request.json['threshold_name']
    minimum, maximum = request.json['min'], request.json['max']

    print request.json

    thermometer = Thermometer.objects.get(device_id=thermometer_id)
    t = ThresholdTrigger(name=threshold_name, min=minimum, max=maximum);
    thermometer.add_temperature_trigger(t)
    thermometer.save()

    return json.dumps(dict(ok=True, result=json.loads(t.to_json())))

@rest_api.route('/threshold/<threshold_id>', methods=['GET'])
def threshold(threshold_id):
    threshold_id = int(threshold_id)
    if request.method == 'GET':
        t = ThresholdTrigger.objects.get(id=threshold_id)
        if t is None:
            resp = dict(ok=True, result="Couldn't find threshold")
        else:
            threshold = json.loads(t.to_json())
            resp = dict(ok=True, result=threshold)
    elif request.method == 'DELETE':
        threshold = ThresholdTrigger.objects(id=threshold_id).first()
        print threshold
        if threshold:
            threshold.delete()
        resp = dict(ok=True, threshold_id=threshold_id)

    return json.dumps(resp)

@rest_api.route('/device/<device_type>', methods=['GET', 'POST'])
def device_types(device_type):
    device_types = []

    for cls in eval(device_type).__subclasses__():
        device_types.append(cls.__name__)

    resp = dict(ok=True, types=device_types)

    return json.dumps(resp)

@rest_api.route('/calendar/create', methods=['POST'])
def create_alarm():
    if request.method == 'POST':
        form = request.form
        day_dico={0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
        s_name, i_hours, i_minutes, m,tu,w,th,f,sa,su = [form.get(val) for val in ['alarm_name', 'hours', 'minutes', 'Monday','Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
        print str(s_name), m,tu,w,th,f,sa,su, i_hours, i_minutes,  int(i_hours)*int(60)+int(i_minutes)
        s_days=[m,tu,w,th,f,sa,su];
        minutes=int(i_hours)*int(60)+int(i_minutes)
        event = model.clock.Event(name=str(s_name), minutes=minutes)
        for day in s_days :
            try :
                event.set_week_day_mask(int(day),True)
            except TypeError :
                print "type error"
        event.save()
        alarms=[{'name':ev.name,'minutes':ev.minutes, 'days':[i for i,day in enumerate([(ev.week_days_mask & (1 << i))!=0 for i in range(7)]) if day==True]} for ev in model.clock.Event.objects()]
        print alarms[0]['days']
    return json.dumps(alarms)


@rest_api.route('/clockConnection', methods=['GET', 'POST'])
def event_clock_binding():

    if request.method == 'GET':
        connections = [dump_connection(c) for c in Connection.objects]
        resp = dict(ok=True, result=connections)
        return json.dumps(resp)

    elif request.method == 'POST':
        s_event =  request.json['event']
        actuator_id, callback = request.json['actuator'], request.json['callback']

        clock = model.clock.Event.objects(name = s_event)
        print s_event
        actuator = Actuator.objects(device_id=actuator_id)
        if len(actuator) == 0 :
            actuator = main_server.rpc_server.RaspiUnit.objects(device_id = actuator_id)
        if len(actuator) > 0 :
            current_app.logger.info(actuator[0].callbacks[callback])
        current_app.logger.info(clock[0].name)

        try:
            connection = clock[0].event.connect(actuator[0].callbacks[callback])
        except ValueError as e:
            resp = dict(ok=False, result=str(e))
            return json.dumps(resp)

        connection_json = dump_connection(connection)
        connection_json['triggering_event'] = s_event

        resp = dict(ok=True, result=connection_json)
        return json.dumps(resp)




@rest_api.route('/calendar/bind', methods = ['GET'])
def bind_music():
    alarm_name = request.args.get("alarm_name")
    print alarm_name
    clock = model.clock.Event.objects(name = alarm_name)
    rpi = main_server.rpc_server.RaspiUnit.objects(name="rpi0")
    print rpi[0].name
    if len(clock) != 0:
        try:
            clock[0].event.connect(rpi[0].callback_rpi_music)
        except ValueError as e:
            resp = dict(ok=False, result=str(e))
            return json.dumps(resp)
    return ""


def dump_alarm(alarm):
    s_json = json.loads(alarm.to_json())
    s_json['days']= [i for i,day in enumerate([(alarm.week_days_mask & (1 << i))!=0 for i in range(7)]) if day==True]
    s_json['events'] = alarm.events.keys()
    s_json['type'] = alarm.__class__.__name__

    # TODO : find a way to render the alarm without putting this into each alarm's data
    listObjects = list(Actuator.objects)
    [listObjects.append(c) for c in main_server.rpc_server.RaspiUnit.objects]
    s_json['actuators'] = [dump_actuator(actuator) for actuator in listObjects]
    print s_json['actuators']
    # TODO : Dirty hack to get events' name
    connections = list()
    for e_name, e in alarm.events.iteritems():
        e_connections = [dump_connection(c) for c in Connection.objects(triggering_event=e)]

        for c in e_connections:
            c['triggering_event'] = e_name

        connections.extend(e_connections)

    s_json['connections'] = connections


    return s_json

@rest_api.route('/alarm/<device_name>', methods=['DELETE'])
def alarm(device_name):
    device_name = str(device_name)
    if request.method == 'DELETE':
        print "<<<<>>>>> " + device_name
        clockEvent = model.clock.Event.objects(name=device_name).first()
        print clockEvent
        if clockEvent:
            clockEvent.delete()
        resp = dict(ok=True, device_name=device_name)

    return json.dumps(resp)


@rest_api.route('/alarms', methods=['POST', 'GET'])
def all_alarms():
    if request.method == 'GET':
        result = [dump_alarm(alarm) for alarm in model.clock.Event.objects]
        resp = dict(ok=True, result=result)

    return json.dumps(resp)
