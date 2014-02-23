#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('..')
sys.path.append('../../libs')

from flask import Flask, render_template
import mongoengine

from enocean.devices import Sensor, Actuator
from model.devices import NumericReading
import model.clock

from reuters import reuters


from config import GlobalConfig
config = GlobalConfig()

news_api = reuters.APIReuters()

## Initializing the app
app = Flask(__name__)
app.debug = True
user = "Adrien"

# Binding the API calls
from api import rest_api
app.register_blueprint(rest_api)

## Main pages
@app.route('/')
def index():
    return render_template('index.html', user=user)

@app.route('/setup')
def setup():
    actuators = Actuator.objects()
    sensor_types = Sensor.__subclasses__()

    return render_template('setup.html', sensor_types=sensor_types, actuators=actuators)

@app.route('/monitoring')
def monitoring():
    reading_classes = NumericReading.__subclasses__()
    return render_template('monitoring.html', reading_classes=reading_classes)

@app.route('/news')
def news():
    articles = {}
    for category in reuters.category_list:
        articles[category] = reuters.Article.objects(category=category)[:10]
    return render_template('news.html', categories = reuters.category_list, articles = articles)


@app.route('/house')
def house():
    return render_template('house.html')

@app.route('/music')
def music():
    combo_options = ["jazz", "rock", "rap", "happy", "sad", "tired"] #TODO this in the config file ?
    size_tags = int(round(len(combo_options)/2))
    left_tags = [i for i in combo_options[:size_tags]]
    right_tags = [i for i in combo_options[size_tags:int(2*size_tags)]]
    return render_template("music.html", combo_options = combo_options, user = user, left_tags = left_tags, right_tags = right_tags)

@app.route('/meteo')
def meteo_page():
    return render_template('meteo.html')

@app.route('/fashion')
def fashion_page():
    return render_template('fashion.html')

@app.route('/product/')
def products():
    products = json.loads(Product.objects.to_json())
    result = dict(ok=True, result=products)
    return json.dumps(result)

@app.route('/calendar')
def calendar():
    day_dico={0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
    #  if len(sys.argv) > 1:
    #     config = GlobalConfig.from_json(sys.argv[1])
    # database = mongoengine.connect(config.mongo_db)

    actuators = Actuator.objects()
    sensor_types = Sensor.__subclasses__()
    alarms=[{'name':ev.name,'minutes':ev.minutes, 'days':[day_dico[i] for i,day in enumerate([(ev.week_days_mask & (1 << i))!=0 for i in range(7)]) if day==True]} for ev in model.clock.Event.objects()]

    return render_template('clock.html', alarms = alarms , sensor_types=sensor_types, actuators=actuators)

if __name__ == "__main__":
    if len(sys.argv) > 1: 
        config = GlobalConfig.from_json(sys.argv[1])
    db = mongoengine.connect(config.mongo_db)

    app.run(host="0.0.0.0", port=config.web_server.port, debug=True)
