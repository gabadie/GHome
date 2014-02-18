#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import locale
sys.path.append('..')
sys.path.append('../../libs')

from flask import Flask, render_template
import mongoengine

from enocean.devices import Sensor, Actuator
from model.fashion import Product
from model.devices import NumericReading
import model.clock

from feedzilla import feedzilla

from config import GlobalConfig
config = GlobalConfig()
news_api = feedzilla.APIFeedzilla()

## Initializing the app
app = Flask(__name__)
app.debug = True

# Binding the API calls
from api import rest_api
app.register_blueprint(rest_api)

## Main pages
@app.route('/')
def index():
    return render_template('index.html')

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
    # category_id = news_api.categories()[0].id
    # category_name = news_api.categories()[0].englishName
    # articles = news_api.articles(category_id)
    # #articles_dump = [json.dumps(article.__dict__) for article in articles]
    # return render_template('news.html', category = category_name, articles=articles)
    categories = news_api.categories()
    return render_template('news.html', categories = categories)


@app.route('/news/<category_id>')
def newsCategory(category_id):
    # category_id = news_api.categories()[0].id
    category_name = news_api.categorieById(int(category_id)).englishName
    articles = news_api.articles(category_id)
    # #articles_dump = [json.dumps(article.__dict__) for article in articles]
    return render_template('newsCategory.html', category_name = category_name, articles = articles)


@app.route('/house')
def house():
    return render_template('house.html')

@app.route('/music')
def music():
    user="Adrien"
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
    #  if len(sys.argv) > 1:
    #     config = GlobalConfig.from_json(sys.argv[1])
    # database = mongoengine.connect(config.mongo_db)
    return render_template('clock.html', alarms = model.clock.Event.objects())

if __name__ == "__main__":
    if len(sys.argv) > 1: 
        config = GlobalConfig.from_json(sys.argv[1])
    db = mongoengine.connect(config.mongo_db)

    app.run(host="0.0.0.0", port=config.web_server.port, debug=True)
