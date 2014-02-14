import mongoengine

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
