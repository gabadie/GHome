#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, '..')

import datetime
import mongoengine
import random

from config import GlobalConfig
config = GlobalConfig()

from enocean.devices import Thermometer, Switch, Lamp, WindowContact
from model.devices import Temperature

def init(config):
    """ For testing only """
    db = mongoengine.connect(config.mongo_db)
    db.drop_database(config.mongo_db)

    # Actuators
    l1 = Lamp(device_id=889977, name='The main lamp', turned_on=True).save()
    l2 = Lamp(device_id=85654, name='Another lamp').save()

    # Sensors
    Thermometer(device_id=1337, name='Living room thermometer', ignored=False).save()
    Thermometer(device_id=4242, name='Bedroom thermometer', ignored=False).save()
    Thermometer(device_id=233232, name='Kitchen thermometer', ignored=False).save()
    Thermometer(device_id=151718, name='Patio thermometer', ignored=False).save()
    Thermometer(device_id=161625, name='Exterior temperature', ignored=False).save()



    Switch(device_id=343830, name='A switch that should work', ignored=False, actuators=[l1, l2]).save()
    Switch(device_id=939400, name='An ignored switch', ignored=True).save()

    WindowContact(device_id=3311, name='A window contact sensor', open=False, ignored=True).save()

    # Readings
    cur_date = datetime.datetime.now()
    cur_temp = 28.0
    time_delta = datetime.timedelta(hours=3)
    for i in xrange(100):
        for j, thermometer in enumerate(Thermometer.objects()):

            temp = cur_temp - j * 2 - 0.9 * (random.random() - 0.5)

            Temperature(device=thermometer, date=cur_date, value=temp).save()

            print "Added temperature reading {} at {}.".format(cur_temp, cur_date)

        cur_temp -= 0.1
        cur_date -= time_delta

if __name__ == '__main__':
    if len(sys.argv) > 1:
        config = GlobalConfig.from_json(sys.argv[1])
    init(config)
