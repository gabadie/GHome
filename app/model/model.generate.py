#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine
import random
from random import randrange
import sys

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
            
    def generate_sensors(self, device_class, device_number, readings_number):
        for i in range(0, device_number):
            device = device_class(device_id=self.unique_id, ignored=False)
            device.save()
            self.generate_readings(device, readings_number)
            
    def generate_readings(self, device, readings_number):
        if isinstance(device, enocean.devices.Thermometer):
            self.generate_thermometer_readings(device, readings_number)
            
        elif isinstance(device, enocean.devices.Switch):
            self.generate_switch_readings(device, readings_number)
            
        elif isinstance(device, enocean.devices.WindowContact):
            self.generate_wc_readings(device, readings_number)
            
        elif isinstance(device, enocean.devices.LightMovementSensor):
            self.generate_lms_readings(device, readings_number)
            
        else:
            raise NotImplementedError
            
    def generate_thermometer_readings(self, device, readings_number):
        for i in range(0, readings_number):
            model.devices.Temperature(device=device, value=round(random.random()*5+17, 2)).save()
            model.devices.Humidity(device=device, value=round(random.random()*50+25, 2)).save()

    def generate_switch_readings(self, device, readings_number):
        for i in range(0, readings_number):
            pressed = random.choice([True, False])
            if pressed:
                model.devices.SwitchState(device=device, side=randrange(2)+1, direction=randrange(2)+3, pressed=pressed).save()
            else:
                model.devices.SwitchState(device=device, side=enocean.devices.Switch.UNKNOWN, direction=enocean.devices.Switch.UNKNOWN, pressed=pressed).save()

    def generate_wc_readings(self, device, readings_number):
        for i in range(0, readings_number):
            model.devices.WindowState(device=device, value=random.choice([True, False])).save()

    def generate_lms_readings(self, device, readings_number):
        for i in range(0, readings_number):
            model.devices.Voltage(device=device, value=round(random.random()*2+3, 2)).save()
            model.devices.Brightness(device=device, value=round(random.random()*200+200)).save()
            model.devices.Movement(device=device, value=random.choice([True, False])).save()
        
    @property
    def unique_id(self):
        self.id += 1
        return self.id

if __name__ == "__main__":
    configuration = GlobalConfig()

    if len(sys.argv) > 1:
        configuration = GlobalConfig.from_json(sys.argv[1])

    generator = ModelGenerator(configuration)
    
    generator.generate_sensors(enocean.devices.Thermometer, 2, 20)
    generator.generate_sensors(enocean.devices.Switch, 2, 5)
    generator.generate_sensors(enocean.devices.WindowContact, 1, 10)
    generator.generate_sensors(enocean.devices.LightMovementSensor, 1, 20)
    
    #idem capteur presence + 3 lampes
