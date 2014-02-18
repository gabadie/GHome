import mongoengine
from datetime import datetime

class Location(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    latitude = mongoengine.FloatField(required=True)
    longitude = mongoengine.FloatField(required=True)
    hoursdelta = mongoengine.IntField(default=0)


class Weather(mongoengine.Document):
    expire = mongoengine.DateTimeField(required=True)
    temperature = mongoengine.FloatField(required=True)
    humidity = mongoengine.FloatField(required=True)
    icon = mongoengine.StringField(required=True)

def get_current_weather():
    #Update current weather
    weather = Weather.objects.first()
    if weather and Weather.objects.first().expire > datetime.now():
        return weather
    elif update_current_weather():
        return Weather.objects.first()

def update_current_weather():
    pass
    # TODO : Needs to be implemented to update the weather
