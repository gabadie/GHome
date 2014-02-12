import mongoengine

class Location(mongoengine.Document):
    name = mongoengine.StringField(required=True)
    latitude = mongoengine.FloatField(required=True)
    longitude = mongoengine.FloatField(required=True)


class Weather(mongoengine.Document):
    expire = mongoengine.DateTimeField(required=True)
    temperature = mongoengine.FloatField(required=True)
    himidity = mongoengine.FloatField(required=True)
