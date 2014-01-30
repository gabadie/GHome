#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import random
from random import randrange
import sys
import datetime

sys.path.insert(0, '..')

import enocean.devices
import model.devices
from config import GlobalConfig

class ModelGenerator:
    def __init__(self, config):
            self.config = config
            self.db = mongoengine.connect(config.mongo_db)
            self.db.drop_database(config.mongo_db)
            self.id = 1337
            
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
        
    @property
    def unique_id(self):
        self.id += 1
        return self.id

if __name__ == "__main__":
    configuration = GlobalConfig()

    if len(sys.argv) > 1:
        configuration = GlobalConfig.from_json(sys.argv[1])

    generator = ModelGenerator(configuration)
    
    #Thermometer
    devices = generator.generate_devices(enocean.devices.Thermometer, 3)
    generator.generate_readings(devices[0], 5, 60)
    generator.generate_reading_evolution(devices[1], model.devices.Temperature, 10, 15, 2, 60)
    generator.generate_reading_evolution(devices[2], model.devices.Humidity, 10, 62, 6, 60)
    
    #Switch
    devices = generator.generate_devices(enocean.devices.Switch, 2)
    generator.generate_readings(devices[0], 5, 120)
    devices = generator.generate_devices(enocean.devices.WindowContact, 1)
    generator.generate_readings(devices[0], 10, 1800)
    
    #LightMovementSensor
    devices = generator.generate_devices(enocean.devices.LightMovementSensor, 1)
    generator.generate_readings(devices[0], 20, 300)
    generator.generate_reading_evolution(devices[0], model.devices.Brightness, 24, 50, 20, 900)
    
    #Lamp
    devices = generator.generate_devices(enocean.devices.Lamp, 3)
    
    #Socket
    devices = generator.generate_devices(enocean.devices.Socket, 1)
