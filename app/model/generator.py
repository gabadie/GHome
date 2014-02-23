#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import random
from random import randrange
import sys
import datetime

sys.path.append('..')

import enocean.devices
import model.devices
from model.trigger import ThresholdTrigger
from model.house import Room
from model.meteo import Location
from model.clock import Event
from config import GlobalConfig
from main_server.rpc_server import RpcServer
from fashion import fetch_fashion

class Generator:
    def __init__(self, config):
            self.config = config
            self.db = mongoengine.connect(config.mongo_db)
            self.db.drop_database(config.mongo_db)
            self.id = 1337

    def generate_location(self, name, lat, lon):
        Location(name=name, latitude=lat, longitude=lon).save()


    def generate_devices(self, device_class, device_number):
        sensors = []
        for i in range(0, device_number):
            device = device_class(device_id=self.unique_id, name="Generated{}".format(device_class.__name__), ignored=False)
            device.save()
            sensors.append(device)
        return sensors

    def generate_readings(self, device, readings_number, quantum):
        """
        Generates random thermometer (temperature and humidity) readings
        @param quantum The time (seconds) elapsed betweed two readings
        """
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)

        if isinstance(device, enocean.devices.Thermometer):
            call = self.generate_thermometer_readings
        elif isinstance(device, enocean.devices.Switch):
            call = self.generate_switch_readings
        elif isinstance(device, enocean.devices.WindowContact):
            call = self.generate_wc_readings
        elif isinstance(device, enocean.devices.LightMovementSensor):
            call = self.generate_lms_readings
        else:
            raise NotImplementedError

        for i in range(0, readings_number):
            call(device, time)
            time += td

    def generate_thermometer_readings(self, device, time):
        model.devices.Temperature(device=device, value=round(random.random()*5+17, 2), date=time).save()
        model.devices.Humidity(device=device, value=round(random.random()*50+25, 2), date=time).save()

    def generate_switch_readings(self, device, time):
        pressed = random.choice([True, False])
        if pressed:
            model.devices.SwitchState(device=device, date=time, side=randrange(2)+1, direction=randrange(2)+3, pressed=pressed).save()
        else:
            model.devices.SwitchState(device=device, date=time, side=enocean.devices.Switch.UNKNOWN, direction=enocean.devices.Switch.UNKNOWN, pressed=pressed).save()

    def generate_wc_readings(self, device, time):
        model.devices.WindowState(device=device, date=time, value=random.choice([True, False])).save()

    def generate_lms_readings(self, device, time):
        model.devices.Voltage(device=device, date=time, value=round(random.random()*2+3, 2)).save()
        model.devices.Brightness(device=device, date=time, value=round(random.random()*200+200)).save()
        model.devices.Movement(device=device, date=time, value=random.choice([True, False])).save()

    def generate_reading_evolution(self, device, reading_class, readings_number, init_value, max_step_evolution, quantum):
        """
        Generates temperature or humidity readings, increasing or decreasing with a specified quantum
        @param reading_class The given class must be an instance of NumericReading (i.e. a class which can be stored in the database with a numeric value)
        @param quantum The time (seconds) elapsed betweed two readings
        """
        value = init_value
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)

        for i in range(0, readings_number):
            reading_class(device=device, value=value, date=time).save()
            value = value + round(random.random()*max_step_evolution, 2)
            time += td

    def generate_alarm(self,name,hours,minutes,days): #days : [1,2,5] for days 1, 2 and 5
        Event.objects.create(name=name, minutes=hours*60+minutes)
        obj = Event.objects(name=name)[0]
        for day in days :
            obj.set_week_day_mask(day,True)
        obj.save()

    def generate_sample(self):
        #Thermometer
        thermometers = self.generate_devices(enocean.devices.Thermometer, 3)
        self.generate_readings(thermometers[0], 10, 60)
        self.generate_reading_evolution(thermometers[1], model.devices.Temperature, 10, 10, -1, 60)
        self.generate_reading_evolution(thermometers[1], model.devices.Humidity, 10, 62, 6, 60)
        self.generate_reading_evolution(thermometers[2], model.devices.Temperature, 10, 15, 2, 60)
        self.generate_reading_evolution(thermometers[2], model.devices.Humidity, 10, 40, -4, 60)

        ## Temperature triggers
        for idx, t in enumerate(thermometers):
            for i in xrange(5):
                trigger = ThresholdTrigger(name="Threshold{}{}".format(idx, i),
                                           min=(idx * 10 + i), max=(2 * idx * 10 + i + 1))
                t.add_temperature_trigger(trigger)
                t.save()


        #Switch
        switches = self.generate_devices(enocean.devices.Switch, 2)
        self.generate_readings(switches[0], 5, 120)

        #Windows Contactor
        wc = self.generate_devices(enocean.devices.WindowContact, 1)
        self.generate_readings(wc[0], 10, 1800)

        #LightMovementSensor
        lms = self.generate_devices(enocean.devices.LightMovementSensor, 2)
        self.generate_readings(lms[0], 24, 900)
        self.generate_reading_evolution(lms[1], model.devices.Brightness, 24, 50, 20, 900)
        self.generate_reading_evolution(lms[1], model.devices.Voltage, 24, 1, 0.25, 900)

        #Lamp
        lamps = self.generate_devices(enocean.devices.Lamp, 3)

        #Socket
        sockets = self.generate_devices(enocean.devices.Socket, 2)

        #Event binding
        #Switches and sockets
        RpcServer.xmlrpc_bind_devices(switches[0].device_id, 'onclick_top_right', sockets[0].device_id, 'callback_toggle')
        RpcServer.xmlrpc_bind_devices(switches[0].device_id, 'onclick_top_left', sockets[1].device_id, 'callback_toggle')

        #Switches and lamps
        RpcServer.xmlrpc_bind_devices(switches[1].device_id, 'onclick_top_right', lamps[0].device_id, 'callback_toggle')
        RpcServer.xmlrpc_bind_devices(switches[1].device_id, 'onclick_bottom_right', lamps[1].device_id, 'callback_toggle')
        RpcServer.xmlrpc_bind_devices(switches[1].device_id, 'onclick_top_left', lamps[2].device_id, 'callback_toggle')

        #switch_id = int("0021CBE5", 16)
        #switch = enocean.devices.Switch(device_id=switch_id, name="THESWITCH", ignored=False)
        #switch.save()

        wc_id = int("0001B592", 16)
        wc = enocean.devices.WindowContact(device_id=wc_id, name="BindedWindowContactor", ignored=False)
        wc.save()


        socket_id = int("FF9F1E04", 16)
        socket = enocean.devices.Socket(device_id=socket_id, name="BindedSocket", ignored=False)
        socket.save()
        #self.rpc_server.xmlrpc_bind_devices(switch_id, 'onclick_top_right', socket_id, 'callback_toggle')
        RpcServer.xmlrpc_bind_devices(wc_id, 'on_opened', socket_id, 'callback_deactivate')
        RpcServer.xmlrpc_bind_devices(wc_id, 'on_closed', socket_id, 'callback_activate')

        # Generating rooms
        self.generate_rooms()

        #Setting current location
        self.generate_location(name="Villeurbanne, France", lat=45.771944, lon=4.8901709)

        #generate alarms
        self.generate_alarm("Work", 6,42,[0,1,2,3,4])
        self.generate_alarm("Music lesson", 17,29,[4])
        self.generate_alarm("GHome presentation", 8,10,[2])

    def generate_rooms(self):
        Room(x=-2.5, y=-2.5, width=5, height=5).save()
        Room(x=+2.5, y=-2.5, width=5, height=4).save()


    @property
    def unique_id(self):
        self.id += 1
        return self.id

if __name__ == '__main__':
    configuration = GlobalConfig()


    if len(sys.argv) > 1 and sys.argv[1] != 'fashion':
        configuration = GlobalConfig.from_json(sys.argv[1])
    g = Generator(configuration)
    g.generate_sample()


    if 'fashion' in sys.argv:
        fetch_fashion()
