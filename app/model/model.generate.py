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
            self.id = 0
        
            enocean.devices.Thermometer(device_id=1337, name='Living room thermometer', ignored=False).save()
            
    def generate_sensors(self, device_class, device_number, readings_number, quantum):
        sensors = []
        for i in range(0, device_number):
            device = device_class(device_id=self.unique_id, ignored=False)
            device.save()
            self.generate_readings(device, readings_number, quantum)
            sensors.append(device)
        return sensors
            
    def generate_readings(self, device, readings_number, quantum):
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
            
        call(device, readings_number, quantum)
            
    def generate_thermometer_readings(self, device, readings_number, quantum):
        """
        Generates random thermometer (temperature and humidity) readings
        @param quantum The time (seconds) elapsed betweed two readings
        """
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)
        
        for i in range(0, readings_number):
            model.devices.Temperature(device=device, value=round(random.random()*5+17, 2), date=time).save()
            model.devices.Humidity(device=device, value=round(random.random()*50+25, 2), date=time).save()
            time += td

    def generate_switch_readings(self, device, readings_number, quantum):
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)
        
        for i in range(0, readings_number):
            pressed = random.choice([True, False])
            if pressed:
                model.devices.SwitchState(device=device, side=randrange(2)+1, direction=randrange(2)+3, pressed=pressed).save()
            else:
                model.devices.SwitchState(device=device, side=enocean.devices.Switch.UNKNOWN, direction=enocean.devices.Switch.UNKNOWN, pressed=pressed).save()
            time += td

    def generate_wc_readings(self, device, readings_number, quantum):
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)
        
        for i in range(0, readings_number):
            model.devices.WindowState(device=device, value=random.choice([True, False])).save()
            time += td

    def generate_lms_readings(self, device, readings_number, quantum):
        time = datetime.datetime.now()
        td = datetime.timedelta(seconds=quantum)
        
        for i in range(0, readings_number):
            model.devices.Voltage(device=device, value=round(random.random()*2+3, 2)).save()
            model.devices.Brightness(device=device, value=round(random.random()*200+200)).save()
            model.devices.Movement(device=device, value=random.choice([True, False])).save()
            time += td
            
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
    
    sensors = generator.generate_sensors(enocean.devices.Thermometer, 2, 1, 60)
    generator.generate_reading_evolution(sensors[0], model.devices.Temperature, 10, 15, 2, 60)
    generator.generate_reading_evolution(sensors[1], model.devices.Humidity, 10, 62, 6, 60)
    
    generator.generate_sensors(enocean.devices.Switch, 2, 5, 120)
    generator.generate_sensors(enocean.devices.WindowContact, 1, 10, 1800)
    
    sensors = generator.generate_sensors(enocean.devices.LightMovementSensor, 1, 20, 300)
    generator.generate_reading_evolution(sensors[0], model.devices.Brightness, 24, 50, 20, 900)
    
    #idem capteur presence + 3 lampes
