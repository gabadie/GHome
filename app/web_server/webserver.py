#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from twisted.web.wsgi import WSGIResource
from twisted.web.server import Site
from twisted.internet import reactor
import mongoengine

import sys
sys.path.insert(0, '..')

from model import core
from enocean.devices import Thermometer

from config import GlobalConfig

config = GlobalConfig()

app = Flask(__name__)
app.debug = True

db = mongoengine.connect(config.mongo_db)
# TODO : remove this, for testing only
db.drop_database(config.mongo_db)

@app.route('/')
def index():
	devices = core.Device.objects()
	return render_template('index.html', devices=devices)

@app.route('/hello')
def hello():
    return 'Hello World'

if __name__ == "__main__":
	# Creating a couple devices to test the DB
	Thermometer(device_id='1337', name='Living room thermometer', ignored=False).save()
	Thermometer(device_id='4242', name='Bedroom thermometer', ignored=True).save()
	Thermometer(device_id='89351', name='Another thermometer', ignored=False).save()
	Thermometer(device_id='34210', name='And yet another thermometer', ignored=False).save()

	app.run(host="localhost", port=5000, debug=True)

	# resource = WSGIResource(reactor, reactor.getThreadPool(), app)
	# site = Site(resource)

	# reactor.listenTCP(5000, site)
	# reactor.run()