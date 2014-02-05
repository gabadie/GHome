#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import mongoengine
import types

sys.path.insert(0, '..')

import logger

class Object(mongoengine.Document):
    meta = {'allow_inheritance': True}

    def save(self):
        for key in self._data:
            value = self._data[key]

            if isinstance(value, Event):
                value.save()

        mongoengine.Document.save(self)

    def delete(self):
        for c in Connection.objects(receiving_object=self):
            c.delete()

        self_attrs_map = self._data
        for key in self_attrs_map:
            value = self_attrs_map[key]

            if isinstance(value, Event):
                value.delete()

        mongoengine.Document.delete(self)

    @property
    def callbacks(self):
        callbacks_map = {}
        self_attrs_map = dir(self)

        for key in self_attrs_map:
            if key.startswith("callback_"):
                value = getattr(self, key)

                if isinstance(value, types.MethodType):
                    callbacks_map[key] = value

        return callbacks_map

    @property
    def events(self):
        events_map = {}
        self_attrs_map = self._data

        for key in self_attrs_map.keys():
            # forces mongoengine to fetch the object from the database to test its type
            value = self.__getattribute__(key)

            if isinstance(value, Event):
                events_map[key] = value

            elif isinstance(value, list):
                for sub_value in value:
                    if isinstance(sub_value, Object) :
                        sub_events_map = sub_value.events
                        key_prefix = "{}.".format(sub_value)

                        for sub_key in sub_events_map.keys():
                            events_map[key_prefix + sub_key] = sub_events_map[sub_key]

        return events_map


class Event(mongoengine.Document):
    def __call__(self, server):
        for callback in Connection.objects(triggering_event=self):
            callback.trigger(server)

    def connect(self, bound_callback):
        obj = bound_callback.__self__
        method_name = bound_callback.__name__
        if Connection.objects(triggering_event=self, receiving_object=obj, method_name=method_name):
            raise ValueError("Connection already exists")

        connection = Connection(triggering_event=self, receiving_object=obj, method_name=method_name)
        connection.save()

        return connection

    def delete(self):
        for c in Connection.objects(triggering_event=self):
            c.delete()

        super(Event, self).delete()


class Connection(mongoengine.Document):
    triggering_event = mongoengine.ReferenceField(Event, required=True)
    receiving_object = mongoengine.ReferenceField(Object, required=True)
    method_name = mongoengine.StringField()

    def trigger(self, server):
        class_content = self.receiving_object.__class__.__dict__

        if self.method_name not in class_content:
            logger.error("Can not trigger event connection: {}.{} have been removed...".format(self.receiving_object.__class__.__name__, self.method_name))
            raise ValueError

        class_content[self.method_name](self.receiving_object, server)

def slot():
    return mongoengine.ReferenceField(Event, required=True, default=Event)

class Trigger(Object):
    name = mongoengine.StringField(required=True)

    def __str__(self):
        return self.name

class ThresholdTrigger(Trigger):

    # Events
    underflow = slot()
    overflow  = slot()

    min = mongoengine.fields.IntField(required=True)
    max = mongoengine.fields.IntField(required=True)

    # Returns whether a event has been triggered
    def trigger(self, oldValue, newValue, server):
        if oldValue < self.max and newValue > self.max:
            self.overflow(server)
            return True
        elif oldValue > self.min and newValue < self.min:
            self.underflow(server)
            return True
        return False


# def IntervalTrigger(Trigger):

#     # Events
#     enterInFromAbove = slot()
#     enterInFromBelow = slot()
#     aboveInterval = slot()
#     belowInterval = slot()

#     def __init__(self, name, min, max):
#         super(Trigger, self).__init__(name)
#         self.min = min
#         self.max = max

#     def trigger(self, oldValue, newValue, server):
#         # if we were inside the interval
#         if self.min <= oldValue <= self.max:
#             if newValue > self.max:
#                 self.aboveInterval(server)
#                 return True
#             elif newValue < self.min:
#                 self.belowInterval(server)
#                 return True
#         # else if we are inside the interval now
#         elif self.min <= newValue <= self.max:
#             if oldValue > self.max:
#                 self.enterInFromAbove(server)
#                 return True
#             if oldValue < self.min:
#                 self.enterInFromBelow(server)
#                 return True

#         return False


