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
                    if isinstance(sub_value, Object):
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

        if len(Connection.objects(triggering_event=self, receiving_object=obj, method_name=method_name)) > 0:
            return

        connection = Connection(triggering_event=self, receiving_object=obj, method_name=method_name)
        connection.save()

    def delete(self):
        for c in Connection.objects(triggering_event=self):
            c.delete()

        mongoengine.Document.delete(self)


class Connection(mongoengine.Document):
    triggering_event = mongoengine.ReferenceField(Event, required=True)
    receiving_object = mongoengine.ReferenceField(Object, required=True)
    method_name = mongoengine.StringField()

    def trigger(self, server):
        class_content = self.receiving_object.__class__.__dict__

        if self.method_name not in class_content:
            logger.error("Can not trigger event connection: {}.{} have been removed...".format(self.receiving_object.__class__.__name__, self.method_name))
            raise NotImplemented

        class_content[self.method_name](self.receiving_object, server)

def slot():
    return mongoengine.ReferenceField(Event, required=True, default=Event)
