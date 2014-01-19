#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mongoengine

class Object(mongoengine.Document):
    meta = {'allow_inheritance': True}

    def delete():
        for c in Connection.objects(event_object=self):
            c.delete()

        mongoengine.Document.delete(self)

    @property
    def events(self):
        events_map = {}
        self_attrs_map = self._data

        for key in self_attrs_map:
            value = self_attrs_map[key]

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
    def trigger(self):
        for callback in Connection.objects(triggering_event=self):
            callback.trigger()

    def connect(self, bound_callback):
        obj = bound_callback.__self__
        method_name = bound_callback.__name__

        if len(Connection.objects(triggering_event=self, receiving_object=obj, method_name=method_name)) > 0:
            return

        connection = Connection(triggering_event=self, receiving_object=obj, method_name=method_name)
        connection.save()


class Connection(mongoengine.Document):
    triggering_event = mongoengine.ReferenceField(Event, required=True)
    receiving_object = mongoengine.ReferenceField(Object, required=True)
    method_name = mongoengine.StringField()

    def trigger(self):
        self.receiving_object.__class__.__dict__[self.method_name](self.receiving_object)


def callback(func):
    def wrapped(self):
        return func()



    return wrapped
