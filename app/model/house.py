import mongoengine

class Room(mongoengine.Document):
    x = mongoengine.FloatField(required=True)
    y = mongoengine.FloatField(required=True)
    width = mongoengine.FloatField(required=True)
    height = mongoengine.FloatField(required=True)
